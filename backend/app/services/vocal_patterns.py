PACE_BANDS = [
    (120, "Slow, Deliberate Pace"),
    (170, "Conversational Pace"),
    (200, "Fast Pace"),
    (float("inf"), "Very Fast Pace"),
]

PAUSE_BANDS = [
    (4, "Few Pauses"),
    (15, "Natural Pausing"),
    (float("inf"), "Frequent Pausing"),
]

PITCH_BANDS = [
    (2.0, "Steady Pitch"),
    (4.0, "Moderate Pitch Variation"),
    (float("inf"), "Expressive Pitch Variation"),
]

def pick_name(value: float, bands: list) -> str:
    for upper_limit, name in bands:
        if value < upper_limit:
            return name
    return bands[-1][1]


def make_vocal_pattern(name: str, description: str, evidence: str, youtube_url: str) -> dict:
    return {
        "channel": "vocal",
        "pattern_name": name,
        "description": description,
        "quote_or_evidence": evidence,
        "timestamp_sec": None,
        "timestamp_label": None,
        "deep_link": youtube_url,
    }

def build_vocal_patterns(metrics: dict, youtube_url: str) -> list[dict]:
    patterns = []
    wpm = metrics.get("words_per_min")

    # Pace
    if wpm:
        patterns.append(make_vocal_pattern(
            pick_name(wpm, PACE_BANDS),
            f"The speaker talks at about {wpm:.0f} words per minute. "
            "Typical conversational speech is roughly 120 to 170 words per minute.",
            f"Pace: {wpm:.0f} words/min (typical conversational range: 120-170)",
            youtube_url,
        ))
    
    # Pauses
    per_min = metrics.get("pauses_per_min")

    if per_min is not None:
        long_count = metrics.get("long_pause_count", 0)
        avg_len = metrics.get("avg_pause_length_sec", 0.0)
        if metrics.get("pause_count", 0) == 0:
            description = "No pauses of 0.3 seconds or longer were detected."
        else:
            description = (
                f"Pauses of 0.3 seconds or longer happen about {per_min:.1f} times per minute, "
                f"averaging {avg_len:.1f} seconds. {long_count} lasted a second or more."
            )
        
        patterns.append(make_vocal_pattern(
            pick_name(per_min, PAUSE_BANDS),
            description,
            f"Pauses: {per_min:.1f} per min, average {avg_len:.1f} s, long pauses (1 s or more): {long_count}",
            youtube_url,
        ))
    
    # pitch
    semitones = metrics.get("pitch_variation_semitones")
    if semitones:
        patterns.append(make_vocal_pattern(
            pick_name(semitones, PITCH_BANDS),
            f"The speaker's pitch moves about {semitones:.1f} semitones (piano keys) around their usual pitch. "
            "Below roughly 2 sounds steady, above roughly 4 sounds lively.",
            f"Pitch variation: {semitones:.1f} semitones (typical range: 2.0-4.0)",
            youtube_url,
        ))

    return patterns




