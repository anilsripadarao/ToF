# Data collect Example

## Requirements
* Default Configuration and calibration files are in "sdk/config" folder

## Command Line Options

```
Usage:
	data_collect.py [-h] [-f FOLDER] [-n NCAPTURE] [-m MODE]
                       [-wt WARMUP_TIME] [--ccb <FILE>] [--ip IP]
                       [-fw FIRMWARE]
                       [-ft {depth,ab,conf,metadata,full-frame,ir}]
                       config

    Arguments:
      FILE            Input config_default.json

    Optional arguments:
		-h, --help            	show this help message and exit
		-f FOLDER             	output folder [default: ./]
		-n NCAPTURE           	number of frame captured [default: 1]
		-m MODE               	Valid mode (-m) options are:
									0: short-range native;
									1: long-range native;
									2: short-range Qnative;
									3: long-range Qnative
									4: pcm-native;
									5: long-range mixed;
									6: short-range mixed

									Note: --m argument supports both index and string [default:0/sr-native]
		-wt WARMUP_TIME       	warmup time in seconds[default: 0]
		--ccb <FILE>          	The path to store CCB content
		--ip IP               	camera IP[default: 10.42.0.1]
		-fw FIRMWARE          	Adsd3500 firmware file
		-ft {depth,ab,conf,metadata,full-frame,ir}
								FrameType of saved image[default: full-frame]
 
``` 

## Run
To run this python example, run data_collect.exe with provided configuration file (which contains paths to camera calibration and camera configuration) and other options in command line inputs. Some example commands can be seen below.

```
python data_collect.py "config/config_adsd3500_adsd3100.json"
python data_collect.py -f "./data_output" config/config_adsd3500_adsd3100.json
python data_collect.py -f "./data_output" -m 10 config/config_adsd3500_adsd3100.json
python data_collect.py -f "./data_output" -n 50 config/config_adsd3500_adsd3100.json
python data_collect.py -f "./data_output" -m sr-native -n 50 -ft full-frame -config/config_adsd3500_adsd3100.json
python data_collect.py -f "./data_output" -m 10 -n 4 -wt 5 config/config_adsd3500_adsd3100.json
```
