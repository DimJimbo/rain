# rain
Terminal rain effect, optionally overlayed over the output of a command, made with python <3

## Usage

* Basic usage, with my presets and without a command in the background
  ```
  python rain.py
  ```
  
* I've made it to be as configurable as possible, here's all the options
  ```
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
  ```
  For a medium-light rain effect, the preset works fine

* Example with a command in the background
  ```
  python rain.py -b "fastfetch --pipe --logo none"
  ```

## TODO

* Add multiple presets for heavy, light, medium etc rain
* Add code that makes a drop bigger when it collides with another one
* O P T I M I Z A T I O N
