import pyaudio
import wave
import time
import threading
import queue
import os


class RealTimeWavPlayer:
    """
    A class for playing WAV chunks in real-time
    """

    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.audio_queue = queue.Queue(maxsize=100)
        self.is_playing = False
        self.play_thread = None
        self.sample_width = None
        self.channels = None
        self.sample_rate = None
        self.format = None

    def set_audio_format(self, sample_width, channels, sample_rate):
        """Set the audio format parameters"""
        self.sample_width = sample_width
        self.channels = channels
        self.sample_rate = sample_rate

        # Map sample width to PyAudio format
        format_mapping = {
            1: pyaudio.paInt8,
            2: pyaudio.paInt16,
            3: pyaudio.paInt24,
            4: pyaudio.paInt32,
        }
        self.format = format_mapping.get(sample_width, pyaudio.paInt16)

    def extract_wav_info(self, wav_file):
        """Extract audio format information from a WAV file"""
        with wave.open(wav_file, "rb") as wf:
            self.set_audio_format(
                wf.getsampwidth(), wf.getnchannels(), wf.getframerate()
            )
            return wf.getsampwidth(), wf.getnchannels(), wf.getframerate()

    def _play_worker(self):
        """Worker thread that plays audio chunks from the queue"""
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.chunk_size,
        )

        self.stream.start_stream()

        while self.is_playing:
            try:
                chunk = self.audio_queue.get(timeout=0.5)
                if chunk is None:  # None is the signal to stop
                    break
                self.stream.write(chunk)
                self.audio_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error playing audio: {e}")
                break

        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.is_playing = False

    def start(self):
        """Start the audio playback thread"""
        if self.is_playing:
            return

        if not all([self.sample_width, self.channels, self.sample_rate]):
            raise ValueError(
                "Audio format not set. Call set_audio_format() or extract_wav_info() first."
            )

        self.is_playing = True
        self.play_thread = threading.Thread(target=self._play_worker)
        self.play_thread.daemon = True
        self.play_thread.start()

    def add_chunk(self, chunk):
        """Add an audio chunk to the playback queue"""
        if self.is_playing:
            try:
                self.audio_queue.put(chunk, block=False)
                return True
            except queue.Full:
                return False
        return False

    def stop(self):
        """Stop the audio playback"""
        if not self.is_playing:
            return

        self.is_playing = False
        self.audio_queue.put(None)  # Signal to stop
        if self.play_thread:
            self.play_thread.join(timeout=1.0)

        # Clear the queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.task_done()
            except queue.Empty:
                break

    def close(self):
        """Clean up resources"""
        self.stop()
        self.p.terminate()


# Example usage 1: Playing chunks from a WAV file in real-time
def example_play_from_file(wav_file):
    player = RealTimeWavPlayer()
    sample_width, channels, sample_rate = player.extract_wav_info(wav_file)
    print(
        f"Playing {wav_file} - Format: {sample_width*8}bit, {channels} channels, {sample_rate}Hz"
    )

    player.start()

    with wave.open(wav_file, "rb") as wf:
        chunk = wf.readframes(player.chunk_size)
        while chunk:
            # Simulate real-time processing by adding small delays
            time.sleep(0.01)  # Adjust this value to simulate different processing times
            player.add_chunk(chunk)
            chunk = wf.readframes(player.chunk_size)

    # Wait for all chunks to be played
    time.sleep(0.5)
    player.stop()
    player.close()


# Example usage 2: Generating and playing chunks dynamically
def example_generate_and_play():
    import numpy as np

    player = RealTimeWavPlayer()
    sample_width = 2  # 16-bit
    channels = 1  # mono
    sample_rate = 44100  # CD quality

    player.set_audio_format(sample_width, channels, sample_rate)
    player.start()

    # Generate a 5-second sine wave tone at 440Hz (A4 note)
    duration = 5.0
    tone_freq = 440.0

    # Generate in chunks
    chunk_duration = player.chunk_size / sample_rate
    num_chunks = int(duration / chunk_duration)

    for i in range(num_chunks):
        t = np.arange(i * player.chunk_size, (i + 1) * player.chunk_size) / sample_rate
        tone = (np.sin(2 * np.pi * tone_freq * t) * 32767).astype(np.int16)
        chunk = tone.tobytes()
        player.add_chunk(chunk)
        time.sleep(
            chunk_duration * 0.8
        )  # Slightly shorter than real-time to avoid buffer underruns

    time.sleep(0.5)
    player.stop()
    player.close()


if __name__ == "__main__":

    wav_file = input("Path to wav file: ").strip()

    if os.path.exists(wav_file):
        example_play_from_file(wav_file)
    else:
        print(f"File {wav_file} not found. Generating tone instead.")
        example_generate_and_play()
