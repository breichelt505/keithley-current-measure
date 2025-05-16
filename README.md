This python based command line tool allows you to make current readings from a Keithley 6517B electrometer and save them to a csv. 

Getting this tool to work requires 3 steps:
1.  Install the [KUSB-488B device driver](https://www.tek.com/en/support/datasheets-manuals-software-downloads) to your machine in order to allow communication with the keithley device.
2.  Set up an environment to run python in with the dependencies in the environment.yml file (python is of course also required). I use anaconda for this with the command ```conda env create -f environment.yml``` but if you wish you can use pip and translate the requirements file as required.
3.  Install some form of VISA on your machine-- NI VISA is what I used but PyVISA-Py is another option-- you may have to adjust the code to change the backend if you use PyVISA-py as described [here](https://pyvisa.readthedocs.io/en/latest/introduction/getting.html)

Once everything is set up, turn on the electrometer and connect to your computer. Then navigate to the project directory in a terminal using the project environment: ```cd /path/to/keithley-current-measure```. Running is as simple as entering the command:

```python src/keithley.py```

This will connect to the keithley, initialize it appropriately, and begin taking measurements that will be displayed on an updating graph. NOTE: DO NOT TURN ON THE CURRENT SOURCE YOU ARE MEASURING UNTIL THE PROGRAM HAS BEGUN RECORDING DATA, OTHERWISE INITIALIZATION MAY BE OFF. When you have finished taking data, exit the program simply by using ctrl+c. At this point, the program will create a .csv file with the data in the ```./outputs/``` directory (it will create this directory automatically if needed) with the timestamp of the first measurement as the name. There are several options you can control and discover using the command 

```python src/keithley.py -h```

If you are having trouple getting your computer to communicate with the Keithley, I recommend you follow the steps [here](https://download.tek.com/manual/KUSB-488B-903-01_Sept2018_KUSB-488B-903-01B.pdf) in order to install the keithley diagnostic tool.
