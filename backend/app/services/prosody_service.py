import librosa
import numpy as np

def extract_prosody_features(audio_path:str) -> dict:
    y, sr = librosa.load(audio_path)
    intervals = librosa.effects.split(y, top_db=30)
    
    total_duration = len(y) / sr
    voiced_duration = sum((end - start) for start, end in intervals) / sr
    speech_ratio = voiced_duration / total_duration if total_duration else 0.0
    
    pauses = []
    for i in range(1, len(intervals)):
        gap_samples = intervals[i][0] - intervals[i-1][1]
        pauses.append(gap_samples / sr)
    
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    voiced_pitches = pitches[magnitudes > np.median(magnitudes)]
    
    return {
        "speech_ratio": round(speech_ratio, 3),
        "pause_count": len(pauses),
        "avg_pause_length_sec": round(float(np.mean(pauses)), 3) if pauses else 0.0,
        "avg_pitch_variation": round(float(np.std(voiced_pitches)), 3) if len(voiced_pitches) else 0.0,
    }