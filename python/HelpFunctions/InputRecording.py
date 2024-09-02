import threading
import pyaudio
import wave
import numpy as np

class InputRecording:
    def __init__(self, filename, sample_rate=44100, channels=1, chunk_size=1024, volume = 1):
        self.filename = filename
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.volume = volume

    def startRecording(self):
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  frames_per_buffer=self.chunk_size)
        self.frames = []
        self.recording = True
        self.thread = threading.Thread(target=self._record)
        self.thread.start()
        print("Recording started...")

    def _record(self):
        while self.recording:
            data = self.stream.read(self.chunk_size)
            audio_data = np.frombuffer(data, dtype=np.int16)
            adjusted_audio_data = np.clip(audio_data * self.volume * 100, -32768, 32767).astype(np.int16)
            self.frames.append(adjusted_audio_data.tobytes())

    def stopRecording(self):
        self.recording = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print("Recording stopped and saved to", self.filename)
