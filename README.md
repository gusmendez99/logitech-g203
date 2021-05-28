# Logitech G203 Prodigy - Driver
Driver Project - OS extras

## Demo
![demo](https://github.com/gusmendez99/logitech-g203/raw/main/images/demo.gif?raw=true)

## Requirements

- Python 3.8+
- PyUSB 1.0.2+
  
**EXTRA - Root privileges**

You need to install PyUSB: `sudo apt-get install python3-usb`


## Usage

```
py driver.py solid {color}                          Solid color mode
py driver.py cycle {rate} {brightness}              Cycle through all colors
py driver.py breathe {color} {rate} {brightness}    Single color breathing
py driver.py intro {on|off}                         Enable/disable startup effect
py driver.py dpi {dpi}                              Set mouse dpi
```

Previous commands needs some params:
- Color: RRGGBB (RGB hex value)
- Rate: 100-60000 (Number of milliseconds. Default: 10000ms)
- Brightness: 0-100 (Percentage. Default: 100%)
- DPI: 200-8000 (Prodigy), 50-8000 (Lightsync) 