# memory_engine.py
# Handles storing and retrieving user interaction history

import json
from datetime import datetime
from pathlib import Path

MEMORY_FILE = "memory.json"

def load_memory():
    """Load memory from file"""
    if not Path(MEMORY_FILE).exists():
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    """Save memory back to file"""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def add_to_memory(user_input, intent, mood):
    """Store a single interaction"""
    memory = load_memory()

    memory.append({
        "time": datetime.now().isoformat(),
        "text": user_input,
        "intent": intent,
        "mood": mood
    })

    save_memory(memory)

def get_recent_context(n=3):
    """Get last n interactions"""
    memory = load_memory()
    return memory[-n:]