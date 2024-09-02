namespace EAProject.Examples
{
    // Calibrates input channel and save the new sensitivity to "Input Channels.xml"
    class Input_calibration
    {
        public static void Main()
        {
            var engine = new EAProject.EA_Engine();
            
            // selecting the 3670 device resets all the channels metadata. This should therefore only be used in the beginning.
            engine.Select3670Device();
            engine.SetInputChannel(1, "4189", true, sensitivity: 50, dbRef: 20e-6);

            engine.RunInputCalibration(1, duration: 5);
        }
    }
}
