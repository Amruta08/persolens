# Groups whisper's per-word timestamps into readable chunks
def format_transcript_with_timestamps(words: list[dict], chunk_size: int = 12) -> str:
    lines = []
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i+chunk_size] # Slice out the next 12 words
        start_time = chunk[0]["start"] # timestamp of the FIRST word in this chunk
        text = " ".join(w["word"] for w in chunk) # stitch the words back into a sentence fragment
        lines.append(f'[{start_time:.1f}s] "{text}"')
    return "\n".join(lines)


# Turn raw librosa numbers into a short sentence the LLM can read directly
def format_prosody_summary(prosody: dict) -> str:
    return(
        f"Speech ratio (talking time / total time): {prosody['speech_ratio']:.2f}\n"
        f"Average pause length: {prosody['avg_pause_length_sec']:.2f} seconds\n"
        f"Pitch variation (higher = more vocal expressiveness): {prosody['avg_pitch_variation']:.2f}"
    )
    