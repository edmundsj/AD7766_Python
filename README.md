# Python SCPI Interface for AD7766
This contains an Arduino sketch for communicating with the AD7766 via an Arduino using [SCPI commands](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments) with python.

## Getting Started
1. Turn on power to the ADC
2. Turn on power to the TIA
3. Plug in the Teensy
4. Turn on and start the optical chopper
5. Run unit tests in this directory with ``python -m unittest discover``. All tests should pass and the noise PSD will be reported. It should be around 260nV/rtHz. If all tests pass, you are ready to run an experiment. If the tests do not pass, go to the "debugging" section.
6. Run the desired scripts from the "examples" directory. 

## Debugging
- Did you try to read more than 600K samples? A hardware issue of unknown origin is preventing that.

## Features
- SCPI Communication with Arduino-based devices
- Python interface requests data from the arduino using standard SCPI commands
- Data stored in numpy arrays and written to .csv files
- Documented on readthedocs ([link](https://python-scpi-ad7766.readthedocs.io/en/latest/))

## Getting Started
I assume you know how to use git. If not, you can download the files you need directly off the git website. I also assume you are familiar with the Arduino and Arduino IDE and have it installed on your PC.
