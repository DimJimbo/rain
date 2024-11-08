import subprocess
import random
import curses
import time
import sys


SPAWN_CHANCE = 50
SPAWN_INERT_CHANCE = 80 
INERT_LIFETIME = 5 
CHANGE_SPEED_CHANCE = 10

CHAR = "o"
TRAIL_LENGTH = 40
TRAIL_CHAR = "|"
MAX_SPEED = 3
MIN_SPEED = 0
UPDATE_INTERVAL = 0.1

COMMAND = ""

HELP = '''
Terminal rain effect

Usage: rain [-hniSscdtlu] [-b COMMAND ]

Note:
	All chances are expected to be percentages ( i.e. 50 for 50% )
	All "speeds" are in characters moved per step

Options:
    -h, --help: show this message

    -n, --SPAWN-CHANCE N: Chance a drop will spawn
    -i, --SPAWN-INERT-CHANCE N: Chance that a spawned drop will be Inert ( i.e. does not move )
    
    -S, --MAX-SPEED N: Maximum speed a drop can have
    -s, --MIN-SPEED N: Minimum speed a drop can have
    -c, --CHANGE-SPEED-CHANCE N: Chance that a drop changes its speed value

    -d, --CHAR STR: Character to use for the drop
    -t, --TRAIL-CHAR STR: Character to use for the trail of a drop
    -L, --TRAIL-LENGTH N: Length of the trail of a drop ( in characters )

    -u, --UPDATE-INTERVAL N: Wait N seconds before updating screen ( N can be a float )
    -l, --INERT-LIFETIME N: After N seconds, an Inert Drop will vanish

    -b, --BACKGROUND COMMAND: Execute COMMAND in the background, while the rain effect plays
'''

# Parse arguments ( I hate argparse formatting an I'm too lazy for making my own formatter)

# Defaults

SPAWN_CHANCE = 50
SPAWN_INERT_CHANCE = 80  
CHANGE_SPEED_CHANCE = 10

CHAR = "o"
TRAIL_LENGTH = 40
TRAIL_CHAR = "|"
MAX_SPEED = 3
MIN_SPEED = 0
UPDATE_INTERVAL = 0.1
INERT_LIFETIME = 5

l = len(sys.argv)
i = 1
while i < l:
    arg = sys.argv[i]
    if arg in ["-h", "--help"]:
        print(HELP)
        exit(0)
    elif arg in ["-n", "--SPAWN-CHANCE"]:
        i += 1
        SPAWN_CHANCE = int(sys.argv[i])
    elif arg in ["-i", "--SPAWN-INERT-CHANCE"]:
        i += 1
        SPAWN_INERT_CHANCE = int(sys.argv[i])
    elif arg in ["-S", "--MAX-SPEED"]:
        i += 1
        MAX_SPEED = int(sys.argv[i])
    elif arg in ["-s", "--MIN-SPEED"]:
        i += 1
        MIN_SPEED = int(sys.argv[i])
    elif arg in ["-c", "--CHANGE-SPEED-CHANCE"]:
        i += 1
        CHANGE_SPEED_CHANCE = int(sys.argv[i])
    elif arg in ["-d", "--CHAR"]:
        i += 1
        CHAR = sys.argv[i]
    elif arg in ["-t", "--TRAIL-CHAR"]:
        i += 1
        TRAIL_CHAR = int(sys.argv[i])
    elif arg in ["-b", "--BACKGROUND"]:
        i += 1
        COMMAND = sys.argv[i]

    i += 1



def chance(odds):
    return random.randint(0, 100) < odds

class InertDrop:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spawn_time = time.time()

class ActiveDrop:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

        self.trail = [] # Previous points, where the y of the last point minus the y of the first ( trail[-1][1] - trail[0][1] ) is less than TRAIL_LENGTH
        self.trail_length = 0 # Trail length (in characters)

    def move(self):
        if chance(CHANGE_SPEED_CHANCE):
            self.speed = random.randint(0, MAX_SPEED)

        if self.speed > 0:
            offst = random.randint(-1, 1) # -1 = down left, 0 = down, +1 = down-right

            self.trail.append((self.x, self.y))
            self.trail_length += self.speed

            self.y += self.speed
            self.x += offst

        if self.trail_length > TRAIL_LENGTH:
            if len(self.trail) > 1:
                self.trail_length -= self.trail[1][1] - self.trail[0][1]
                self.trail.pop(0)
            elif len(self.trail) == 1:
                self.trail_length -= self.y - self.trail[0][1]
                self.trail.pop(0)

class Screen:
    def __init__(self):
        self.scr = curses.initscr()
        self.height, self.width = self.scr.getmaxyx()

        curses.noecho()
        curses.curs_set(0)

        self.active_drops = []
        self.inert_drops = []
        

    def __del__(self):
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

    def drawCommandOut(self):

        proc = subprocess.run(COMMAND, shell=True, capture_output=True)
        
        proc_out = proc.stdout.strip()
        self.scr.addstr(0, 0, proc_out)

            
    def drawDrops(self):
        for drop in self.inert_drops:
            try:
                self.drawDrop(drop)
            except Exception as e: # curses is a bit buggy, idk why some exceptions still happen soo just ignore
                pass
                
        for drop in self.active_drops:
            try:
                self.drawDrop(drop)
                self.drawDropTrail(drop)
            except Exception as e: # curses is a bit buggy, idk why some exceptions still happen soo just ignore
                pass

    def drawDrop(self, drop):
        if 0 <= drop.x < self.width and 0 <= drop.y < self.height:
            self.scr.addstr(drop.y, drop.x, CHAR)

    def drawDropTrail(self, drop):
        prev_y = drop.trail[0][1] # the y of the first trail char, best way to ensure y - gprev_y == 0
        for x, y in drop.trail:
            if 0 <= x < self.width and 0 <= y < self.height:
                for i in range(prev_y, y):
                    self.scr.addstr(i, x, TRAIL_CHAR)
            prev_y = y

        # Also draw a trail from the last position to the Drops current
        if 0 <= drop.x - 1 < self.width and 0 <= drop.y - 1 < self.height:
            for i in range(drop.trail[-1][1], drop.y):
                self.scr.addstr(i, drop.x, TRAIL_CHAR)

    def addDrop(self):
        x = random.randint(0, self.width)

        if chance(SPAWN_INERT_CHANCE):
            y = random.randint(0, self.height)
            self.inert_drops.append(InertDrop(x, y))
        else:
            speed = random.randint(1, MAX_SPEED) # start at speed >= 1, bc a drop with speed = 0 at the top doesnt really add anything
            y = 0
            
            self.active_drops.append(ActiveDrop(x, y, speed))

    def delInertDrop(self, index):        
        self.inert_drops.pop(index)

    def delActiveDrop(self, index):
        self.active_drops.pop(index)

    def updateDrops(self):
        if chance(SPAWN_CHANCE):
            self.addDrop()

        i = 0
        l = len(self.active_drops)
        while i < l:
            drop = self.active_drops[i]
            if drop.y - drop.trail_length > self.height:
                self.delActiveDrop(i)
                l -= 1
            else:
                
                drop.move()
                

            i += 1

    def mainloop(self):
        while True:
            
            self.updateDrops()
            # self.handleDropCollisions()

            self.scr.erase()

            self.drawCommandOut()
            
            time.sleep(UPDATE_INTERVAL)
            self.drawDrops()
            self.scr.refresh()

scr = Screen()
scr.mainloop()
