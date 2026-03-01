"""
Think of this like a chief of staff who sits between you and a team of specialists.
You tell them what you need in plain English. They figure out which specialist
to call, collect the results, and come back with a coherent answer.

This is the most complex file in the project because it handles
a multi-turn conversation loop with tool use — Claude may need to
call multiple tools in sequence before it can answer your request.

The loop:
  1. Send user message + available tools to Claude
  2. Claude either responds directly OR requests a tool call
  3. If tool call → execute it → feed result back → go to 1
  4. If direct response → done, return to user
"""

import json
import anthropic
from src.config        import ANTHROPIC_API_KEY, CLAUDE_MODEL
from src.tools         import ALL_TOOLS
from src.tool_executor import execute_tool


# System prompt — tells Claude who it is and how to behave
SYSTEM_PROMPT = """You are a personal assistant with access to the user's Gmail and Google Calendar.

You can:
- Read and search emails
- Send emails on the user's behalf
- Check upcoming calendar events
- Create new calendar events

Guidelines:
- Be concise and direct
- When sending emails, confirm the key details in your response
- When reading emails, summarize clearly — don't dump raw content
- For multi-step tasks, explain what you're doing at each step
- Today's date is available from the calendar — use it for relative time references
- Always be helpful and proactive"""


class Assistant:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print("[Assistant] Ready.")

    def chat(self, user_message: str, conversation_history: list = None) -> dict:
        """
        Process a user message, executing any tool calls Claude requests.

        conversation_history: list of previous messages for multi-turn context.
        Each message is {"role": "user"|"assistant", "content": "..."}

        Returns:
          - response:  Claude's final text response
          - tools_used: list of tool names that were called
          - history:   updated conversation history
        """
        # Build message history — start fresh or continue existing conversation
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})

        tools_used = []

        # ── The tool use loop ─────────────────────────────────
        # This loop is the core of the agentic pattern.
        # Claude may need multiple tool calls to complete one request.
        # e.g. "Check my calendar and email Sarah my availability"
        # requires: get_upcoming_events → then send_email
        while True:
            response = self.client.messages.create(
                model      = CLAUDE_MODEL,
                max_tokens = 2000,
                system     = SYSTEM_PROMPT,
                tools      = ALL_TOOLS,
                messages   = messages
            )

            # ── Case 1: Claude wants to use a tool ────────────
            if response.stop_reason == "tool_use":
                # Extract all tool use blocks from the response
                tool_use_blocks = [
                    block for block in response.content
                    if block.type == "tool_use"
                ]

                # Add Claude's response (including tool requests) to history
                messages.append({
                    "role":    "assistant",
                    "content": response.content
                })

                # Execute each tool and collect results
                tool_results = []
                for tool_use in tool_use_blocks:
                    print(f"[Assistant] Claude requested tool: {tool_use.name}")
                    tools_used.append(tool_use.name)

                    result = execute_tool(tool_use.name, tool_use.input)

                    # Tool results must be returned in this exact format
                    # The tool_use_id links the result back to the request
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": tool_use.id,
                        "content":     json.dumps(result)
                    })

                # Feed all tool results back to Claude in one message
                messages.append({
                    "role":    "user",
                    "content": tool_results
                })
                # Loop continues — Claude will now reason over the results

            # ── Case 2: Claude has a final response ───────────
            elif response.stop_reason == "end_turn":
                # Extract the text response
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text

                # Add final response to history for future turns
                messages.append({
                    "role":    "assistant",
                    "content": final_text
                })

                return {
                    "response":    final_text,
                    "tools_used":  tools_used,
                    "history":     messages
                }

# The while True loop is the key pattern here —
# it keeps running until Claude returns end_turn instead of tool_use.
# This is what allows Claude to chain multiple tools in one request.
# For "check my calendar and email Sarah my availability"
# Claude calls
# - get_upcoming_events,
# - gets the results,
# - then calls send_email,
# - gets confirmation,
# - then finally returns end_turn with a summary.
# All in one user message.