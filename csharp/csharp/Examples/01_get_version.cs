namespace EAProject.Examples
{
    // Gets the current version of EA Engine
    class Get_version
    {
        public static void Main()
        {
            var engine = new EAProject.EA_Engine();
            Console.WriteLine(engine.GetEngine().GetVersion());
        }
    }
}
