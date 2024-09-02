using EA_Engine;

namespace EAProject.Examples
{
    // Runs a swept sine test
    class Swept_sine_test
    {
        public static void Main()
        {
            var engine = new EAProject.EA_Engine();
            engine.DeselectWdmInputDevice();
            engine.SetAllChannelsToFalse();
            engine.SetInputChannel(1, "4189 Ch.1", true);
            engine.SetOutputChannel(1, "3670-A", true);
            // The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
            var res = engine.RunSweptSineTest(1,
											  duration: 10,
											  startFrequency: 20,
											  endFrequency: 20000,
											  repetition: 0,
											  scanningMode: ScanningModeTypes.Logarithmic);
        }
    }
}
