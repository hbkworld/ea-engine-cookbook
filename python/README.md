# Python example guide

This README will guide you through the setup process as well as how to run the different examples.

## Requirements
1. python >= 3.7
2. Add git to the environment variables

It is recommended to install VSCode, Sublime Text 3, or similar to run and edit the code. To not break any Python installation it is recommended to use either a docker or a Python virtual environment to run the test.

## Setup and how to run an example
To run the given examples the requirements file must be installed. To do this run the following command in your terminal.
```bash
python -m pip install -r requirements.txt
```
After the Python modules are installed you can run the examples found in the examples folder. Simply go to the root of the python folder and run:
```bash
python -m Examples.01_get_version
```
The examples use the class `Engine` found in the HelpFunctions folder. The class contains methods that simplify and automate the process of configure the different test. Feel free to tweak and customize the engine to your liking.

