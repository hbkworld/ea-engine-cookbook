using EA_Engine;

namespace EAProject.Examples
{
    //Runs an Open Loop Random Noise Test which makes the user able to test an output or an input that is not directly connected to the 3670-A. 
    class OpenLoopRandomNoiseTest
    {
        // External Output: The external output plays the stimulus which gets captured by the inputs connected to the 3670-A
        private static void ExternalOutput()
        {
            var engine = new EAProject.EA_Engine();

            // Sets all channels to be inactive
            engine.SetAllChannelsToFalse();

            /* 
			 	In this case we are using the sensitivity from the Head and Torso Simulator.
			    The sensitivity could also be found using input calibration
			 */
            engine.SetInputChannel(1, "Left ear", true, "none", 15.8, "mV/Pa");
            engine.SetInputChannel(2, "Right ear", true, "none", 15.8, "mV/Pa");

            // Selects your wdm device
            engine.SelectWdmOutputDevice("Headphones", true);

            // The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
            var res = engine.RunCompleteOpenLoopRandomNoiseTest(1,
																triggerLevel: 0.2,
																duration: 10,
																lowerFrequency: 20,
																upperFrequency: 20000,
																burstSineLevel: 0.8,
																burstSineFrequency: 1000,
																burstSineCycles: 1000,
																level: 0.5);

        }
        // External Input: The external input records the stimulus played by the output channel of the 3670-A
        private static void ExternalInput()
        {
            var engine = new EAProject.EA_Engine();

            // Sets all channels to be inactive
            engine.SetAllChannelsToFalse();

            engine.SetOutputChannel(1, "3670-A Ch.1", true);

            // Selects your wdm device
            engine.SelectWdmInputDevice("Headset", true);
            // remember to use the correct senitivity for the microphone
            engine.SetInputChannel(9, "Headset", true, sensitivity: 10, sensitivityUnit: "mV/Pa");
            

            // The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
            var res = engine.RunPlaybackOpenLoopRandomNoiseTest(1, duration: 10, lowerFrequency: 20, upperFrequency: 20000);
        }
        public static void Main()
        {
            //ExternalInput();
            ExternalOutput();
        }
    }
}

