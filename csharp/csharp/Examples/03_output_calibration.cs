namespace EAProject.Examples
{
    // Calibrates output channel and save the new sensitivty to "Output Channels.xml"
    class Output_calibration
    {
        public static void Main()
        {
            var engine = new EAProject.EA_Engine();
            engine.SetOutputChannel(1, "3670-A", true);
            engine.RunOutputCalibration(1, 1, frequency: 1000, level: 0.01, duration: 10);
        }
    }
}
