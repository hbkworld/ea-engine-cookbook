from HelpFunctions.Engine import EA_Engine
import HelpFunctions.ea_engine as EA

# Runs a random noise test
if __name__ == "__main__":
    engine = EA_Engine()
    engine.deselectWdmInputDevice()
    engine.setAllChannelsToFalse()
    engine.setInputChannel(1, "4189 Ch.1", True)
    engine.setInputChannel(2, "4189 Ch.2", True)
    engine.setOutputChannel(1, "3670-A", True)
    # Slope of 6 is equal to pink noise
    # The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
    res = engine.runRandomTest(1, duration=10, lowerFrequency=20, upperFrequency=20000,
                               resultFileFormatType=EA.ResultFileFormatTypes.CSV, slope=6, filename="random_test",
                               measurementModeType=EA.MeasurementModeTypes.Spectra)
