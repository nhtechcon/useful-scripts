"""
A simple script for generating sine wave chunks and saving them to WAV files.
"""

import wave
import numpy as np


def generate_sine_chunk(
    frequency, chunk_duration, sample_rate=44100, amplitude=0.5, phase_offset=0
):
    """
    Generate a sine wave chunk as a numpy array

    Args:
        frequency (float): Frequency of the sine wave in Hz
        chunk_duration (float): Duration of the chunk in seconds
        sample_rate (int): Sample rate in Hz
        amplitude (float): Amplitude of the sine wave (0.0 to 1.0)
        phase_offset (float): Phase offset in radians to ensure continuity
                              between chunks

    Returns:
        tuple: (numpy.ndarray of samples, new phase offset)
    """

    # Calculate the number of samples
    num_samples = int(chunk_duration * sample_rate)

    # Generate time values
    t = np.linspace(0, chunk_duration, num_samples, False)

    # Generate sine wave with phase continuity
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t + phase_offset)

    # Calculate phase offset for the next chunk to ensure continuity
    next_phase_offset = (phase_offset + 2 * np.pi * frequency * chunk_duration) % (
        2 * np.pi
    )

    return sine_wave, next_phase_offset


def sine_wave_chunk_generator(
    frequency,
    chunk_duration,
    num_chunks=None,
    sample_rate=44100,
    amplitude=0.5,
):
    """
    Generator that yields sine wave chunks

    Args:
        frequency (float or callable): Frequency in Hz or a function that
                                       takes chunk_index and returns frequency
        chunk_duration (float): Duration of each chunk in seconds
        num_chunks (int, optional): Number of chunks to generate, None for
                                    infinite
        sample_rate (int): Sample rate in Hz
        amplitude (float): Amplitude of the sine wave (0.0 to 1.0)

    Yields:
        numpy.ndarray: Chunk of sine wave samples
    """
    phase_offset = 0
    chunk_index = 0

    while num_chunks is None or chunk_index < num_chunks:
        # Handle frequency as either a fixed value or a function
        if callable(frequency):
            freq = frequency(chunk_index)
        else:
            freq = frequency

        # Generate chunk with phase continuity
        chunk, phase_offset = generate_sine_chunk(
            freq, chunk_duration, sample_rate, amplitude, phase_offset
        )

        yield chunk
        chunk_index += 1


def save_chunked_wav(filename, chunks_generator, sample_rate=44100):
    """
    Save chunks from a generator to a WAV file

    Args:
        filename (str): Output WAV filename
        chunks_generator (generator): Generator yielding audio sample chunks
        sample_rate (int): Sample rate in Hz
    """
    # Open WAV file
    with wave.open(filename, "w") as wav_file:
        # Set parameters
        nchannels = 1  # Mono
        sampwidth = 2  # 16-bit

        # Set initial WAV file parameters (we'll update frames later)
        wav_file.setparams(
            (nchannels, sampwidth, sample_rate, 0, "NONE", "not compressed")
        )

        total_samples = 0

        # Write each chunk as it's generated
        for chunk in chunks_generator:
            # Convert to 16-bit PCM
            max_amplitude = 32767  # Maximum amplitude for 16-bit audio
            chunk_int = (chunk * max_amplitude).astype(np.int16)

            # Write chunk
            wav_file.writeframes(chunk_int.tobytes())

            total_samples += len(chunk)

        # Update the number of frames in the file header
        wav_file._nframes = total_samples


# Example 1: Generate a constant frequency tone in chunks
def example_constant_frequency():
    print("Generating constant frequency tone in chunks...")

    # Parameters
    frequency = 440.0  # A4 note
    chunk_duration = 0.1  # 100ms chunks
    total_duration = 3.0  # 3 seconds total
    num_chunks = int(total_duration / chunk_duration)

    # Generate and save
    chunks = sine_wave_chunk_generator(frequency, chunk_duration, num_chunks)
    save_chunked_wav("constant_tone.wav", chunks)

    print(f"Generated constant_tone.wav ({total_duration}s at {frequency}Hz)")


# Example 2: Generate a frequency sweep using a function to calculate frequency
def example_frequency_sweep():
    print("Generating frequency sweep in chunks...")

    # Parameters
    start_freq = 220.0  # A3 note
    end_freq = 880.0  # A5 note
    chunk_duration = 0.05  # 50ms chunks
    total_duration = 5.0  # 5 seconds total
    num_chunks = int(total_duration / chunk_duration)

    # Frequency function (linear sweep)
    def freq_function(chunk_index):
        # Map chunk_index from [0, num_chunks) to [start_freq, end_freq]
        t = chunk_index / (num_chunks - 1) if num_chunks > 1 else 0
        return start_freq + t * (end_freq - start_freq)

    # Generate and save
    chunks = sine_wave_chunk_generator(
        freq_function,
        chunk_duration,
        num_chunks,
    )
    save_chunked_wav("frequency_sweep.wav", chunks)

    print(f"Generated frequency_sweep.wav (sweep from {start_freq}Hz to {end_freq}Hz)")


# Example 3: Stream infinite chunks to a file until manually stopped
def example_infinite_chunks():
    print(
        "Streaming infinite chunks to a file (limited to 10 chunks for demonstration)..."
    )

    # Parameters
    frequency = 330.0  # E4 note
    chunk_duration = 0.2  # 200ms chunks

    # For demonstration, we'll limit to 10 chunks
    # In a real streaming scenario, you would use a different stopping condition
    chunks = sine_wave_chunk_generator(frequency, chunk_duration, num_chunks=10)
    save_chunked_wav("streamed_tone.wav", chunks)

    print(f"Generated streamed_tone.wav (streaming {frequency}Hz tone)")


if __name__ == "__main__":
    example_constant_frequency()
    example_frequency_sweep()
    example_infinite_chunks()
