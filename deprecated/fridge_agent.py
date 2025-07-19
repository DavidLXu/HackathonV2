#!/usr/bin/env python3
"""Smart Fridge Agent

A single-file prototype that demonstrates how to use Qwen-VL's
function-calling to control a cylindrical smart fridge.

Usage:
    pip install openai pillow
    export OPENAI_API_KEY="sk-..."
    python fridge_agent.py some_food.jpg

The script:
* keeps a JSON record of the fridge contents
* forwards each event to the LLM together with that state
* executes whatever tool calls (`lift`, `turn`, `fetch`) the
  model emits.
"""

import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import openai
from PIL import Image

# ----------------------------------------------------------------------
# Hardware primitives (stub implementations for local testing)
# ----------------------------------------------------------------------

def lift(level_index: int) -> str:
    """Move platform vertically to level_index (0 = bottom)."""
    msg = f"reached level {level_index}"
    print(msg)
    return msg


def turn(section_index: int) -> str:
    """Rotate platform to section_index within current level."""
    msg = f"turned to section {section_index}"
    print(msg)
    return msg


def fetch() -> str:
    """Extend the arm to put in or take out the item."""
    msg = "fetched object"
    print(msg)
    return msg


# ----------------------------------------------------------------------
# Agent implementation
# ----------------------------------------------------------------------

STATE_FILE = Path("fridge_state.json")
DEFAULT_STATE: Dict[str, Any] = {}  # empty fridge

FUNCTION_SIGNATURES = [
    {
        "name": "lift",
        "description": "Move the platform vertically to a target level.",
        "parameters": {
            "type": "object",
            "properties": {
                "level_index": {
                    "type": "integer",
                    "description": "Target level, 0 = coldest bottom.",
                }
            },
            "required": ["level_index"],
        },
    },
    {
        "name": "turn",
        "description": "Rotate the platform to face a section.",
        "parameters": {
            "type": "object",
            "properties": {
                "section_index": {
                    "type": "integer",
                    "description": "Target section within the current level.",
                }
            },
            "required": ["section_index"],
        },
    },
    {
        "name": "fetch",
        "description": "Extend / retract the arm to put in or take out an item.",
        "parameters": {"type": "object", "properties": {}},
    },
]

SYSTEM_TEMPLATE = """You are FridgeAgent, controller of a smart cylindrical fridge.

Geometry:
  * Levels: 0 (coldest, bottom) .. N (warmest, top)
  * Each level has radial sections 0 .. M.

You may call the following tools in any order:
  - lift(level_index: int)
  - turn(section_index: int)
  - fetch()

Current fridge state (JSON):
{state_json}

User preferences (JSON):
{prefs_json}

Event types:
  * "NEW_ITEM": a new item image arrives; decide where to store it.
  * "SUGGEST": user asks what to eat/use next; suggest or retrieve.
  * "TICK": hourly event; proactively suggest if needed.

Think step‑by‑step *silently*. Output either:
  1) tool calls (function_call), or
  2) a final natural‑language assistant message.
"""


class FridgeAgent:
    """Orchestrates LLM reasoning and executes tool calls."""

    def __init__(self, api_key: str, model: str = "qwen-vl-chat"):
        openai.api_key = api_key
        self.model = model
        self.state: Dict[str, Any] = self._load_state()
        self.user_prefs = {
            "likes": ["vegetables", "seafood"],
            "dislikes": ["dairy"],
            "diet": "pescatarian",
        }

    # ---------------- state ----------------
    def _load_state(self) -> Dict[str, Any]:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
        return DEFAULT_STATE.copy()

    def _save_state(self) -> None:
        STATE_FILE.write_text(json.dumps(self.state, indent=2))

    # ---------------- helpers ----------------
    @staticmethod
    def _encode_image(path: str | Path) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def _chat(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        return openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            functions=FUNCTION_SIGNATURES,
            function_call="auto",
        )

    def _run_tool(self, name: str, kwargs: Dict[str, Any]) -> str:
        if name == "lift":
            return lift(**kwargs)
        if name == "turn":
            return turn(**kwargs)
        if name == "fetch":
            return fetch()
        raise ValueError(f"Unknown tool {name}")

    # ---------------- core loop ----------------
    def _agent_loop(self, messages: List[Dict[str, Any]]) -> str:
        while True:
            resp = self._chat(messages)
            msg = resp.choices[0].message

            if msg.get("function_call"):
                call = msg["function_call"]
                name = call["name"]
                args = json.loads(call.get("arguments", "{}"))
                result = self._run_tool(name, args)

                # append tool result and continue
                messages.append(msg)
                messages.append(
                    {"role": "tool", "name": name, "content": result}
                )
                continue
            # natural-language answer
            return msg.get("content", "")

    # ---------------- public API ----------------
    def handle_new_item(self, img_path: str | Path) -> None:
        b64 = self._encode_image(img_path)
        sys_prompt = SYSTEM_TEMPLATE.format(
            state_json=json.dumps(self.state, indent=2),
            prefs_json=json.dumps(self.user_prefs, indent=2),
        )
        messages = [
            {"role": "system", "content": sys_prompt},
            {
                "role": "user",
                "content": "NEW_ITEM",
                "images": [{"type": "base64", "data": b64}],
            },
        ]
        answer = self._agent_loop(messages)
        print("\nAssistant:", answer)
        # NOTE: the assistant can optionally embed JSON info;
        # here we do not parse it for brevity.

    def suggest_item(self) -> None:
        sys_prompt = SYSTEM_TEMPLATE.format(
            state_json=json.dumps(self.state, indent=2),
            prefs_json=json.dumps(self.user_prefs, indent=2),
        )
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": "SUGGEST"},
        ]
        answer = self._agent_loop(messages)
        print("\nAssistant:", answer)

    def tick(self) -> None:
        sys_prompt = SYSTEM_TEMPLATE.format(
            state_json=json.dumps(self.state, indent=2),
            prefs_json=json.dumps(self.user_prefs, indent=2),
        )
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": "TICK"},
        ]
        answer = self._agent_loop(messages)
        print("\nAssistant:", answer)


# ----------------------------------------------------------------------
# CLI entry-point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    key = os.getenv("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    agent = FridgeAgent(key)

    if len(sys.argv) >= 2:
        # treat argument as image path for a new item
        agent.handle_new_item(sys.argv[1])
    else:
        # demo tick
        agent.tick()
