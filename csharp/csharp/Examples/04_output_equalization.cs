namespace EAProject.Examples
{
    // Calibrates output channel and save the new sensitivty to "Output Channels.xml"
    class Output_Equalization
    {
        public static void Main()
        {
            var engine = new EAProject.EA_Engine();
            engine.SetInputChannel(1, "4189 Ch.1", true);
            engine.SetOutputChannel(1, "3670-A", true);
            engine.RunOutputEqualization(1, 1);
        }
    }
}
