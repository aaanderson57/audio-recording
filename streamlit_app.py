import librosa
import numpy as np
import soundfile as sf
import pandas as pd
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from io import BytesIO
from pydub import AudioSegment

#@title Audio File and BPM Input
#audio_file_path = "batidas.m4a" #@param {type:"string"}
#bpm = 128 #@param {type:"number"}


def analyze_beats(audio_data, bpm):
    """
    Analyzes audio data to determine beat positions.

    Args:
        audio_data (bytes): Audio data as bytes.
        bpm (float): Beats per minute.

    Returns:
        pandas.DataFrame: A DataFrame containing beat information.
    """
    try:
        # Convert bytes to AudioSegment
        audio_segment = AudioSegment.from_file(BytesIO(audio_data), format="wav") # Assuming input is WAV
        st.write('Tentando imprimir audio_segment')
        st.write(len(audio_segment))
            
        # Convert AudioSegment to NumPy array
        y = np.array(audio_segment.get_array_of_samples())
        sr = audio_segment.frame_rate
        st.write('y e sr')
        st.write(y, sr)
        
        sr = 0.6*sr
        st.write('antes de onset_strength')
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)
        st.write('antes de beat track')
        tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        st.write('tempo e beat_frames')
        sr.write(tempo, beat_frames)
        beat_times = librosa.frames_to_time(beat_frames, sr=(10/6)*sr)

        pulse_duration = 60 / bpm
        beat_info = []
        first_beat_time = beat_times[0]
        for i, beat_time in enumerate(beat_times):
            beat_number = int((beat_time - first_beat_time) / pulse_duration)
            position_in_pulse = ((beat_time - first_beat_time) % pulse_duration) / pulse_duration
            beat_info.append((beat_time, beat_number, position_in_pulse))

        df = pd.DataFrame(beat_info, columns=['Time (s)', 'Beat Number', 'Position in Pulse'])
        df['Relative Time (s)'] = df['Time (s)'] - df['Time (s)'].iloc[0]
        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

st.title("Beat Analyzer")

bpm = st.number_input("Enter BPM", min_value=1, value=128)

audio_bytes = audio_recorder()
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

if audio_bytes:    
    if st.button("Analyze"):
        beat_data = analyze_beats(audio_bytes, bpm)
        st.write(beat_data)
        if beat_data is not None:
            st.dataframe(beat_data)
else:
    st.warning("Please record an audio file.")
