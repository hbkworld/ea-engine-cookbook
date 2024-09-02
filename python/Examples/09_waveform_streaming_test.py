from HelpFunctions.Engine import EA_Engine
import HelpFunctions.ea_engine as EA

# Runs a waveform streaming test which lets the user choose the signal
if __name__ == "__main__":
    engine = EA_Engine()
    engine.deselectWdmInputDevice()
    engine.setInputChannel(1, "4189", True)
    engine.setOutputChannel(1, "3670-A", True)
    path = "wav_for_streaming.wav"
    # The results from the test will be saved in the res variable. If the plots are active you have to close them before the function returns
    res = engine.runWaveformStreamingTest(1, path, trackIndex=1)
