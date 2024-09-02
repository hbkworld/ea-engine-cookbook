using EA_Engine;

namespace EAProject.Examples
{
    // Runs a random noise test
    class Random_test
    {
        public static void Main()
        {
            var engine = new EAProject.EA_Engine();
            engine.DeselectWdmInputDevice();
            engine.SetAllChannelsToFalse();
            engine.SetInputChannel(1, "4189 Ch.1", true);
            engine.SetOutputChannel(1, "3670-A", true);
            // The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
            var res = engine.RunRandomTest(1,
										   duration: 10,
										   lowerFrequency: 20,
										   upperFrequency: 20000,
										   resultFileFormatType: ResultFileFormatTypes.CSV,
										   slope: 6,
										   filename: "random_test",
										   measurementModeType: MeasurementModeTypes.Spectra,
										   disablePlots: false);
        }
    }
}
