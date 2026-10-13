import librosa
import numpy as np

PAUSE_MIN_SEC = 0.3
LONG_PAUSE_SEC = 1.0
MIN_VOICED_FRAMES = 50



def extract_prosody_features(audio_path:str) -> dict:
    y, sr = librosa.load(audio_path, sr=16000, mono=True)
    total_duration = len(y) / sr
    
    
    intervals = librosa.effects.split(y, top_db=30)
    voiced_duration = sum((end - start) for start, end in intervals) / sr
    speech_ratio = voiced_duration / total_duration if total_duration else 0.0
    
    # Count pauses
    pauses = []
    long_pause_count = 0
    for i in range(1, len(intervals)):
        gap_sec = (intervals[i][0] - intervals[i - 1][1]) / sr
        if gap_sec >= PAUSE_MIN_SEC:
            pauses.append(gap_sec)
            if gap_sec >= LONG_PAUSE_SEC:
                long_pause_count += 1
        
    avg_pause = 0.0
    if pauses:
        avg_pause = float(np.mean(pauses))
    pauses_per_min = 0.0
    if total_duration:
        pauses_per_min = len(pauses) / (total_duration / 60)
    
    
    # pitch
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),  # ~65 Hz, below any normal speaking voice
        fmax=librosa.note_to_hz("C5"),  # ~523 Hz, above any normal speaking voice
        sr=sr,
    )
    
    voiced_f0 = f0[voiced_flag & ~np.isnan(f0)]
    
    pitch_variation = 0.0
    if len(voiced_f0) >= MIN_VOICED_FRAMES:
        semitones = 12 * np.log2(voiced_f0 / np.median(voiced_f0))
        pitch_variation = float(np.std(semitones))
    
    
    return {
        "total_duration_sec": round(float(total_duration), 1),
        "speech_seconds": round(float(voiced_duration), 1),
        "silent_seconds": round(float(total_duration - voiced_duration), 1),
        "speech_ratio": round(float(speech_ratio), 3),
        "pause_count": len(pauses),
        "pauses_per_min": round(pauses_per_min, 2),
        "long_pause_count": long_pause_count,
        "avg_pause_length_sec": round(avg_pause, 3),
        "pitch_variation_semitones": round(pitch_variation, 2),
    }
    
            

# Compute words per minute
def compute_pace(words: list[dict]) -> dict:
    if len(words) < 2:
        return {"word_count": len(words), "words_per_min": 0.0}
    
    span_sec = words[-1]["start"] - words[0]["start"]
    if span_sec <= 0:
        return {"word_count": len(words), "words_per_min": 0.0}
    
    words_per_min = len(words) / (span_sec / 60)
    return {"word_count": len(words), "words_per_min": round(words_per_min, 1)}