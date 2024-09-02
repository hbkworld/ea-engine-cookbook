using EA_Engine;
using NAudio.Wave;

namespace EAProject
{
	public static class Handlers
	{
        public static double timestamp = 0;
        public static (double[], double[])[] dataPoints;
        public static bool frequencyPlotReady = false;
        public static string[,] channelInfo = new string[10,3];
        public static TestResultsAvailableArgs? testResults;

		private static readonly Lazy<Engine> LazyEngine = new Lazy<Engine>(() =>  HelperEngine.GetEngine());
        private static Engine engine = LazyEngine.Value;

        public static void TimeUpdatedHandler(object sender, TimeUpdatedArgs e)
        {
            if (e.CurrentTime < e.Duration)
            {
                Console.Write($"\r{e.CurrentMessage}: {e.CurrentTime:F2}");
                timestamp = e.CurrentTime;
            }
            else
            {
                Console.WriteLine();
            }
        }
        public static void FeedbackHandler(object sender, FeedbackdArgs e)
        {
            Console.WriteLine($"{e.MessageType} - {e.Message}");
        }
        public static void AverageUpdatedHandler(object sender, AverageUpdatedArgs e)
        {
            if (e.CurrentAverage < e.TotalAverages)
            {
                Console.Write($"\rAverage: {e.CurrentAverage} / {e.TotalAverages}");
            }
            else
            {
                Console.Write($"\rAverage: {e.TotalAverages} / {e.TotalAverages}");
                Console.WriteLine();
            }
        }
        public static void TimeDataCallback(object sender, TimeDataRecordedArgs args)
        {
            if (args.TimeBlocks != null)
            {
                var data = args.TimeBlocks;
                if (data.GetLength(0) != 0)
                {
					double[] y = new double[4096];
					for (int i = 0; i < data.GetLength(0); i++)
					{
						y[i] = data[i, 0];
					}
					Buffer.Append(y);
                }
            }
        }
        public static void FftProcessingUpdated(object sender, MultiSIMOFFTProcessingResultsUpdatedArgs args)
        {
            if (args.AutoSpectrum != null)
            {
				dataPoints = new (double[], double[])[args.AutoSpectrumInfo.Length];

				for (int i = 0; i < args.AutoSpectrumInfo.Length; i++)
				{
                    string[] splitInfo  = args.AutoSpectrumInfo[i].Split('|');
                    for (int j = 0; j < splitInfo.Length; j++)
                    {
                        channelInfo[i, j] = splitInfo[j];
                    }
				}
                double[] freq = args.FrequencyAxis;
                var data = args.AutoSpectrum;
                if (freq.Length != 0)
                {
                    for (int i = 0; i < data.GetLength(1); i++)
                    {
                        var x = new double[freq.Length];
                        var y = new double[freq.Length];
                        for (int j = 0; j < freq.Length; j++)
                        {
                            x[j] = freq[j];
                            var test = data[j, i];
                            y[j] = data[j, i];
                        }
                        dataPoints[i] = (x, y);
                    }
                }
            }
            frequencyPlotReady = true;
        }
        public static void StepProcessingUpdated(object sender, HarmonicEstimatorProcessingResultsUpdatedArgs args)
        {

            if (args.SpectrumAmplitude != null)
            {
				dataPoints = new (double[], double[])[args.SpectrumInfo.Length];

				for (int i = 0; i < args.SpectrumInfo.Length; i++)
				{
                    string[] splitInfo  = args.SpectrumInfo[i].Split('|');
                    for (int j = 0; j < splitInfo.Length; j++)
                    {
                        channelInfo[i, j] = splitInfo[j];
                    }
				}
                double[] freq = args.FrequencyAxis;
                var data = args.SpectrumAmplitude;
                if (freq.Length != 0)
                {
                    for (int i = 0; i < data.GetLength(1); i++)
                    {
                        var x = new double[freq.Length];
                        var y = new double[freq.Length];
                        for (int j = 0; j < freq.Length; j++)
                        {
                            x[j] = freq[j];
                            var test = data[j, i];
                            y[j] = data[j, i];
                        }
                        dataPoints[i] = (x, y);
                    }
                }
            }
            frequencyPlotReady = true;
        }
        
        public static void StimulusCreatedHandler(object sender, StimulusCreatedArgs args)
        {
            var outputChannelName = engine.GetSelectedWDMOutputDevice().Name.Replace(" Left", "").Replace(" Right", "");
            int? deviceNumber = null;
            
            for (int i = -1; i < WaveOut.DeviceCount; i++)
            {
                var caps = WaveOut.GetCapabilities(i);
                if (outputChannelName.StartsWith(caps.ProductName))
                {
                    deviceNumber = i;
                    break;
                }
            }

            var wavPath = args.FullPath;
            WaveFileReader wav = new WaveFileReader(wavPath);
            if (deviceNumber == null)
            {
                System.Console.WriteLine("ERROR: Could not find device to play stimulus");
                return;

			}
            var output = new WaveOutEvent{ DeviceNumber = deviceNumber.Value };
            output.Init(wav);
            output.Play();
        }

        public static void TestResultsReadyHandler(object sender, TestResultsAvailableArgs args)
        {
            testResults = null;
            if (args.AutoSpectrum != null)
            {
				dataPoints = new (double[], double[])[args.AutoSpectrumInfo.Length];

				for (int i = 0; i < args.AutoSpectrumInfo.Length; i++)
				{
                    string[] splitInfo  = args.AutoSpectrumInfo[i].Split('|');
                    for (int j = 0; j < splitInfo.Length; j++)
                    {
                        channelInfo[i, j] = splitInfo[j];
                    }
				}
                double[] freq = args.FrequencyAxis;
                var data = args.AutoSpectrum;
                if (freq.Length != 0)
                {
                    for (int i = 0; i < data.GetLength(1); i++)
                    {
                        var x = new double[freq.Length];
                        var y = new double[freq.Length];
                        for (int j = 0; j < freq.Length; j++)
                        {
                            x[j] = freq[j];
                            var test = data[j, i];
                            y[j] = data[j, i];
                        }
                        dataPoints[i] = (x, y);
                    }
                }
				frequencyPlotReady = true;
            }
			testResults = args;
        }
        public static void SaveResultsToVarHandler(object sender, TestResultsAvailableArgs args)
        {
            testResults = args;
        }
	}
}
