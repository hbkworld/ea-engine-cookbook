using EA_Engine;

namespace EAProject.Examples
{
    // Runs a step sine test
    class Step_sine_test
    {
        public static void Main()
        {
            var engine = new EAProject.EA_Engine();
            engine.DeselectWdmInputDevice();
            engine.SetAllChannelsToFalse();
            engine.SetInputChannel(1, "4189 Ch.1", true);
            engine.SetOutputChannel(1, "3670-A", true);
            // The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
            var res = engine.RunStepSineTest(1,
											 startFrequency: 20,
											 endFrequency: 20000,
											 resolutionType: StepSineResolutionTypes.R80,
											 minCycles: 10,
											 minDuration: 0.1,
											 stepIncrement: 1);
        }
    }
}
