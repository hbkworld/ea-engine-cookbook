from HelpFunctions.Engine import EA_Engine
import HelpFunctions.ea_engine as EA

# Runs a equalization of the output channel
if __name__ == "__main__":
    engine = EA_Engine()
    engine.deselectWdmInputDevice()
    engine.setAllChannelsToFalse()
    engine.setInputChannel(1, "4189 Ch.1", True)
    engine.setOutputChannel(1, "3670-A", True)
    # The results from the equalization will be saved in the res variable. If the plots are active you have to close them before the function returns
    res = engine.runOutputEqualization(1, 1, frequencyStart=20, frequencyEnd=20e3, disablePlots=False)

