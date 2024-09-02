using EA_Engine;
using NAudio.Wave;
using EAProject;

namespace csharp.HelpFunctions
{
	internal class InputRecording
	{
		private WaveInEvent waveIn;
		private WaveFileWriter writer;
		private string path;
		private static readonly Lazy<Engine> LazyEngine = new Lazy<Engine>(() =>  HelperEngine.GetEngine());
        private static Engine engine = LazyEngine.Value;

		public InputRecording(string path)
		{
			this.path = path;
		}
		public void StartRecording(int sampleRate)
		{
			waveIn = new WaveInEvent();

			waveIn.WaveFormat = new WaveFormat(sampleRate, 1);
			int? deviceNumber = GetDeviceNumber();
			waveIn.DeviceNumber = deviceNumber.Value;

			waveIn.DataAvailable += OnDataAvailable;
			waveIn.RecordingStopped += OnRecordingStopped;

			writer = new WaveFileWriter(path, waveIn.WaveFormat);

			waveIn.StartRecording();
			Console.WriteLine("Recording started...");
		}

		public void StopRecording()
		{
			waveIn.StopRecording();
		}
		private int? GetDeviceNumber()
		{
			int? deviceNumber = null;
			var inputChannelName = engine.GetSelectedWDMInputDevice().Name;

            for (int i = -1; i < WaveInEvent.DeviceCount; i++)
            {
                var caps = WaveInEvent.GetCapabilities(i);
                if (inputChannelName.StartsWith(caps.ProductName))
                {
                    deviceNumber = i;
                    break;
                }
            }
			return deviceNumber;
		}


		private void OnDataAvailable(object sender, WaveInEventArgs e)
		{
			if (writer != null)
			{
				writer.Write(e.Buffer, 0, e.BytesRecorded);
				writer.Flush();
			}
		}

		private void OnRecordingStopped(object sender, StoppedEventArgs e)
		{
			writer?.Dispose();
			writer = null;
			waveIn.Dispose();
			waveIn = null;

			Console.WriteLine("Recording stopped.");
		}
	}
}
