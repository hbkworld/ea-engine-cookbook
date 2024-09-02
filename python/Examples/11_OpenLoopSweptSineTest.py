import HelpFunctions.ea_engine as EA
from HelpFunctions.Engine import EA_Engine


# Runs an Open Loop Swept Sine Test which makes the user able to test an output or an input that is not directly
# connected to the 3670-A.


# External Output: The external output plays the stimulus which gets captured by the inputs connected to the 3670-A
def externalOutput():
    engine = EA_Engine()

    # Sets all channels to be inactive
    engine.setAllChannelsToFalse()
    """
    In this case we are using the sensitivity from the Head and Torso Simulator.
    The sensitivity could also be found using input calibration
    """
    engine.setInputChannel(1, "Left ear", True, "none", 15.8, "mV/Pa")
    engine.setInputChannel(2, "Right ear", True, "none", 15.8, "mV/Pa")

    # Selects your wdm device
    engine.selectWdmOutputDevice("Headphones", True)

    # The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
    res = engine.RunCompleteOpenLoopSweptSineTest(1, triggerLevel=0.3, level=0.5, sweepTime=10,
                                                  sweepMode=EA.ScanningModeTypes.Logarithmic, repetitions=0,
                                                  startFrequency=20, endFrequency=20000)


# External Input: The external input records the stimulus played by the output channel of the 3670-A
def externalInput():
    engine = EA_Engine()

    # Sets all channels to be inactive
    engine.setAllChannelsToFalse()

    engine.setOutputChannel(1, "3670-A Ch.1", True)

    # Selects your wdm device
    engine.selectWdmInputDevice("Headset", True)
    # remember to use the correct senitivity for the microphone
    engine.setInputChannel(9, "Headset", True, sensitivity=10, sensitivityUnit="mV/Pa")

    # The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
    res = engine.RunPlaybackOpenLoopSweptSineTest(1, sweepTime=10, sweepMode=EA.ScanningModeTypes.Logarithmic,
                                                  repetitions=0, startFrequency=20, endFrequency=20000)


if __name__ == "__main__":
    externalOutput()
    #externalInput()
