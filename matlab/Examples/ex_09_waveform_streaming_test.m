% Runs waveform streaming which lets the user choose the signal
addpath ..\;
engine = Engine();

% Sets all channels to inactive 
engine.deselectWdmInputDevice();
engine.setAllChannelsToFalse();

engine.setInputChannel(1, "4189 Ch.1", true);
engine.setOutputChannel(1, "3670-A", true);

path = "../wav_for_streaming.wav";

% The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
res = engine.runWaveformStreamingTest(1, path, 1);