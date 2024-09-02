import sys
import pythoncom
import clr

pythoncom.CoInitialize()

# EA Engine installation path
installPath = "C:\\Program Files\\HBK\\EA Engine"
# Add the EA Engine .NET assembly (EA Engine executable filename - including full path)
clr.AddReference("C:\\Program Files\\HBK\\EA Engine\\EA_Engine.exe")
# Add the Signal Processing Library .NET assembly (including full path). This one contains some enums and classes that are mandatory to setup the analysis
clr.AddReference("C:\\Program Files\\HBK\\EA Engine\\Signal Processing Library.dll")

# Import the assemblies namespace
from EA_Engine import *
from SignalProcessing.Library import *

# Declare and instanciate a new Engine object (the installation path is mandatory)
# engine = Engine(installPath)

# Import the functions used by handlers
#from Feedback import feedback
#from TimeUpdated import timeupdated
#from AverageUpdated import averageupdated
#from Calfeedback import calfeedback
# from Errormessage import errormessage
# Declare and instanciate a new Engine object (the installation path is mandatory)
engine = Engine(installPath)
curves = [None] * 10
timestamp = 0

withoutHandlersEngine = engine


def getEngine():
    return withoutHandlersEngine

from HelpFunctions.Handlers import Handlers

# Add handlers for a .NET object (here the engine object)
# Events are:
# - Feedback: returns information during a task execution
# - TimeUpdated: returns the time elapsed during data acquisiton
# - AverageUpdated: return the average updated during processing (FFT)
engine.Feedback += Handlers.feedback
engine.TimeUpdated += lambda source, args: Handlers.timeupdated(Handlers, source, args)
engine.AverageUpdated += Handlers.averageupdated


if __name__ == "__main__":
    getEngine()
