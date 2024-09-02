using EA_Engine;

namespace EAProject
{
    class HelperEngine
    {
        public static Engine? engine;
        public static double timestamp = 0;

        public HelperEngine()
        {
            // EA Engine installation path
            string installPath = "C:\\Program Files\\HBK\\EA Engine";

            // Instantiate a new Engine object (the installation path is mandatory)
            engine = new Engine(installPath);
            if (engine == null)
            {
                Console.WriteLine("Failed to initialize EA_Engine");
                Environment.Exit(-1);
            }

            // Add handlers for the .NET object (here the engine object)
            // Events are:
            // - Feedback: returns information during a task execution
            // - TimeUpdated: returns the time elapsed during data acquisition
            // - AverageUpdated: return the average updated during processing (FFT)
            engine.Feedback += Handlers.FeedbackHandler;
            engine.TimeUpdated += Handlers.TimeUpdatedHandler;
            engine.AverageUpdated += Handlers.AverageUpdatedHandler;

        }
        public static Engine GetEngine()
        {
            return engine;
        }
    }
}
