from HelpFunctions.Engine import EA_Engine
import HelpFunctions.ea_engine as EA

# Runs a swept sine test
if __name__ == "__main__":
    engine = EA_Engine()
    engine.deselectWdmInputDevice()
    engine.setInputChannel(1, "4189", True)
    engine.setOutputChannel(1, "3670-A", True)
    # The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
    res = engine.runSweptSineTest(1, duration=10, startFrequency=20, endFrequency=20e3, scanningMode=EA.ScanningModeTypes.Linear, repetition=0)
