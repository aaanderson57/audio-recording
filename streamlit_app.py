import streamlit as st
from audio_recorder_streamlit import audio_recorder
import librosa
import numpy as np
import soundfile as sf


def analyze_beats(audio_file, bpm):
    """
    Analyzes an audio file to determine beat positions relative to a given BPM.

    Args:
        audio_file (str): Path to the audio file (WAV format).
        bpm (float): Beats per minute.

    Returns:
        list: A list of tuples, where each tuple contains:
              - The time of the beat in seconds.
              - The beat number (starting from 0).
              - The position of the beat within the pulse (0.0 to 1.0).
    """

    try:
        # Load the audio file
        y, sr = librosa.load(audio_file, sr = None)
        sr = 0.6*sr
        # The problem seems to be in sampling rate (sr). Setting as sr = 0.1*sr the beats are detected more precisely, but the time increses (why?)
        # Answer: When you set a diferent value to sr, remember to correct to value in input of the function 'librosa.frames_to_time'.
        # For example, setting sr = 0.1*sr you need to correct the input as librosa.frames_to_time(beat_frames, sr = 10*sr)

        # Estimate beat times (2 possible ways). See https://librosa.org/doc/main/generated/librosa.beat.beat_track.html
        # Way 1:
        #tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        #beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        # Way 2:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)
        tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=(10/6)*sr) #100/55 is the adjustment for sr setted before.

        # Calculate pulse duration in seconds
        pulse_duration = 60 / bpm

        beat_info = []
        first_beat_time = beat_times[0]
        for i, beat_time in enumerate(beat_times):
            # Determine the beat number (pulse number) relative to the first beat
            beat_number = int((beat_time - first_beat_time) / pulse_duration)

            # Calculate position within the pulse
            position_in_pulse = ((beat_time - first_beat_time) % pulse_duration) / pulse_duration
            beat_info.append((beat_time, beat_number, position_in_pulse))
        return beat_info

    except FileNotFoundError:
        print(f"Error: Input file '{audio_file}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


audio_bytes = audio_recorder()
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

bpm = 60
beat_data = analyze_beats(audio_bytes, bpm)

if beat_data:
    print("Beat Information:")
    first_beat_time = beat_data[0][0]
    for beat_time, beat_number, position in beat_data:
        relative_beat_time = beat_time - first_beat_time
        print(f"Time: {beat_time:.2f} s, Relative_Time: {relative_beat_time:.2f} s, Beat Number: {beat_number}, Position in Pulse: {position:.2f}")
