import subprocess


class ToolBox:
    def __init__(self):
        pass

    def execute_bash(self, command: str) -> str:
        """
        Executes a standard Linux terminal command and returns the output.
        Designed for grep, ls, cat, etc.
        """
        try:
            # shell=True allows for pipes (|) and redirects (>)
            # capture_output=True grabs both stdout and stderr
            process = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=15
            )
            
            # Combine output and errors so the AI sees the full context
            result = process.stdout + process.stderr
            return result if result.strip() else "Success (no output)."
            
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 15 seconds."
        except Exception as e:
            return f"System Error: {str(e)}"


TOOLS_SCHEMA = [
    {
        "name": "execute_bash",
        "description": "Run a bash command to see files, search text with grep, or check system status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string", 
                    "description": "The full bash command to execute."
                }
            },
            "required": ["command"]
        }
    }
]