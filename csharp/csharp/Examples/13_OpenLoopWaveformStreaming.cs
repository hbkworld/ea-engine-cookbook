namespace EAProject.Examples
{
    //Runs an Open Loop Waveform streaming Test which makes the user able to test an output or an input that is not directly connected to the 3670-A. 
    class OpenLoopWaveformStreaming
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

            // path for the wav file used for streaming
            string fileName = "wav_for_streaming.wav";
            string projectDirectory = AppDomain.CurrentDomain.BaseDirectory;
            string parentDirectory = Directory.GetParent(projectDirectory).Parent.Parent.Parent.FullName;
            string path = Path.Combine(parentDirectory, fileName);

            // The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
            var res = engine.RunCompleteOpenLoopWaveformStreamingTest(path, 1, triggerLevel: 0.3, level: 0.2, trackIndex: 1);
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

            // path for the wav file used for streaming
            string fileName = "wav_for_streaming.wav";
            string projectDirectory = AppDomain.CurrentDomain.BaseDirectory;
            string parentDirectory = Directory.GetParent(projectDirectory).Parent.Parent.Parent.FullName;
            string path = Path.Combine(parentDirectory, fileName);

            // The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
            var res = engine.RunPlaybackOpenLoopWaveformStreamingTest(1, path, trackIndex: 1);
        }
        public static void Main()
        {
            ExternalInput();
            //ExternalOutput();
        }
    }
}
