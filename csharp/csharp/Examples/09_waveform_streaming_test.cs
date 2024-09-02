namespace EAProject.Examples
{
    // Runs a waveform streaming test which lets the user choose the signal
    class Waveform_streaming_test
    {
        public static void Main()
        {
            var engine = new EAProject.EA_Engine();
            engine.DeselectWdmInputDevice();
            engine.SetAllChannelsToFalse();
            engine.SetInputChannel(1, "4189 Ch.1", true);
            engine.SetOutputChannel(1, "3670-A", true);
            string fileName = "wav_for_streaming.wav";
            string projectDirectory = AppDomain.CurrentDomain.BaseDirectory;
            string parentDirectory = Directory.GetParent(projectDirectory).Parent.Parent.Parent.FullName;
            string path = Path.Combine(parentDirectory, fileName);
            // The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
            var res = engine.RunWaveformStreamingTest(1, path, trackIndex: 1);
        }
    }
}
