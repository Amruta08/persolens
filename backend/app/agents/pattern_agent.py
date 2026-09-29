import json
from openai import OpenAI
from app.core.config import settings
from app.agents.schemas import PatternProposals
from app.agents.state import AnalysisState
from app.agents.formatting import format_transcript_with_timestamps, format_prosody_summary

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are analyzing a speaker's communication style from a video transcript.
Identify recurring COMMUNICATION patterns (storytelling, rhetorical technique, structure, filler words)
and VOCAL patterns (pacing, pauses, pitch, emphasis) — using the vocal-metrics summary provided.
Every pattern MUST cite a real timestamp and a real quote from the transcript given to you.
Do not invent patterns that aren't clearly supported by the text. If you see fewer than 2 clear
patterns, it is correct to return fewer — do not pad the list with weak or repeated observations."""


def validate_timestamps(patterns: list[dict], transcript_words: list[dict]) -> list[dict]:
    if not transcript_words:
        return []
    
    last_word_time = transcript_words[-1]["start"]
    
    valid = []
    for p in patterns:
        if 0 <= p["timestamp_sec"] <= last_word_time + 5:
            valid.append(p)
    
    return valid


def propose_patterns(state: AnalysisState) -> dict:
    transcript_text = format_transcript_with_timestamps(state["transcript_words"])
    prosody_text = format_prosody_summary(state["prosody"])
    
    user_prompt = f"""
    TRANSCRIPT (timestamped chunks): 
    {transcript_text}
    
    VOCAL METRICS:
    {prosody_text}
    """
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format=PatternProposals,
    )
    
    parsed: PatternProposals = completion.choices[0].message.parsed
    raw_patterns = [p.model_dump() for p in parsed.patterns] 
    validated = validate_timestamps(raw_patterns, state["transcript_words"])
    
    return {"candidate_patterns": validated}
    

from langgraph.graph import StateGraph, END
graph_builder = StateGraph(AnalysisState)
graph_builder.add_node("pattern_agent", propose_patterns)
graph_builder.set_entry_point("pattern_agent")
graph_builder.add_edge("pattern_agent", END)

pattern_graph = graph_builder.compile()