import os
from dotenv import load_dotenv
from engine import ClaudeEngine
from tools import ToolBox, TOOLS_SCHEMA
from memory import MemoryManager, MEMORY_SCHEMA

# Load API keys from .env file
load_dotenv()

# Combine schemas so Claude sees all available tools
ALL_TOOLS = TOOLS_SCHEMA + [MEMORY_SCHEMA]


def print_block(block):
    if block.type == "thinking":
        print(f"\nTHOUGHT: {block.thinking}")
    elif block.type == "tool_use":
        print(f"\nACTION: {block.name}({block.input})")
    elif block.type == "text":
        print(f"\nCLAUDE: {block.text}")


def main_loop():
    # Initialize our Blocks
    engine = ClaudeEngine(api_key=os.getenv("ANTHROPIC_API_KEY"))
    tools = ToolBox()
    memory = MemoryManager()
    
    # Inject Long-term Memory into the start of the conversation
    mem_context = memory.get_context_string()
    messages = [{"role": "user", "content": f"System Initialization: {mem_context}\nPlease acknowledge what you remember and wait for my command."}]
    
    print("nanoClaw. Type your message and press Enter.")
    print("Type 'exit' or Ctrl+C to quit.\n")

    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if user_input.strip().lower() in {"exit", "quit"}:
            print("Exiting. Goodbye!")
            break

        # Add user message to history
        messages.append({"role": "user", "content": user_input})

        # The "Interleaved Thinking" Loop
        while True:
            response = engine.get_response(messages, ALL_TOOLS)

            assistant_content = []
            tool_use_block = None

            for block in response.content:
                print_block(block)
                if block.type == "thinking":
                    assistant_content.append({
                        "type": "thinking",
                        "thinking": block.thinking,
                        "signature": block.signature
                    })
                elif block.type == "tool_use":
                    tool_use_block = block
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
                elif block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})

            # Save Claude's response (thoughts + tools/text) to history
            messages.append({"role": "assistant", "content": assistant_content})

            # Handle Tool Execution
            if tool_use_block:
                result = ""
                
                # BRANCH 1: Terminal Tools
                if tool_use_block.name == "execute_bash":
                    cmd = tool_use_block.input["command"]
                    result = tools.execute_bash(cmd)
                
                # BRANCH 2: Flat Memory Tool
                elif tool_use_block.name == "save_to_memory":
                    info = tool_use_block.input["info"]
                    result = memory.save_to_memory(info)
                
                print(f"RESULT: {result}")

                # Feed result back to Claude to continue the thought process
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": result
                        }
                    ]
                })
                continue # Return to top of 'while True' to get Claude's next thought
                
            break # Exit inner loop if no more tools are needed


if __name__ == "__main__":
    main_loop()