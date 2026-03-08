import json
import os

class MemoryManager:
    def __init__(self, filepath="memory.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump({"entries": []}, f)

    def load_memory(self):
        with open(self.filepath, "r") as f:
            return json.load(f)

    def save_to_memory(self, info: str) -> str:
        data = self.load_memory()
        # Prevent exact duplicates
        if info not in data["entries"]:
            data["entries"].append(info)
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=4)
            return f"Information remembered: {info}"
        return "I already remember that."

    def get_context_string(self) -> str:
        data = self.load_memory()
        if not data["entries"]:
            return ""
        memories = "\n".join([f"- {item}" for item in data["entries"]])
        return f"\n<memory>\nThings you must remember:\n{memories}\n</memory>"


MEMORY_SCHEMA = {
    "name": "save_to_memory",
    "description": "Use this to save anything important the user says or any system state you should remember across sessions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "info": {"type": "string", "description": "The information to remember."}
        },
        "required": ["info"]
    }
}