#!/usr/bin/env python3
"""Smart Fridge Agent (DashScope Generation API).

Drop‑in replacement of the previous OpenAI version that relies solely
on Alibaba Cloud DashScope SDK – **no openai package required**.

Quick start
-----------
  pip install 'dashscope>=1.23.0' pillow
  export DASHSCOPE_API_KEY="your‑key"
  python fridge_agent_qwen.py demo.jpg   # adds a new item
  python fridge_agent_qwen.py            # hourly tick

Notes
-----
* The script uses :pyclass:`dashscope.Generation` with
  ``result_format='message'`` so we can keep the familiar list‑of‑dict
  chat structure.
* Tools (aka functions) are passed via the ``tools=…`` parameter; set
  ``tool_choice='auto'`` to let Qwen decide when to call them.

Tested with DashScope 1.23.8 (Jul 2025).
"""

import base64
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import dashscope
from dashscope import Generation
from http import HTTPStatus
from PIL import Image
from dashscope import ChatCompletion

# ----------------------------------------------------------------------
# Stub hardware layer (replace with real firmware bindings)
# ----------------------------------------------------------------------

def lift(level_index: int) -> str:
    msg = f"reached level {level_index}"
    print(msg)
    return msg


def turn(section_index: int) -> str:
    msg = f"turned to section {section_index}"
    print(msg)
    return msg


def fetch() -> str:
    msg = "fetched object"
    print(msg)
    return msg


# ----------------------------------------------------------------------
# Agent
# ----------------------------------------------------------------------

STATE_FILE = Path("fridge_state.json")
DEFAULT_STATE: Dict[str, Any] = {}

FUNCTION_SIGNATURES = [
    {
        "name": "lift",
        "description": "Move the platform vertically to a target level.",
        "parameters": {
            "type": "object",
            "properties": {
                "level_index": {"type": "integer", "description": "0 = coldest (bottom)."}
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
                "section_index": {"type": "integer", "description": "Target section index."}
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

SYSTEM_TEMPLATE = """You are **FridgeAgent**, controller of a smart cylindrical fridge.

Geometry:
  • Levels: 0 (coldest, bottom) .. N (warmest, top)
  • Each level has several radial sections 0 .. M.

Available tools:
  - lift(level_index: int)
  - turn(section_index: int)
  - fetch()

Current fridge state (JSON):
{state_json}

User preferences (JSON):
{prefs_json}

Events:
  • "NEW_ITEM": a new item image arrives; decide where to store it and call tools.
  • "SUGGEST": user asks what to eat/use next.
  • "TICK": hourly event for proactive suggestions.

Think silently.  Respond either with **tool calls** or a final natural‑language message.
"""


class FridgeAgent:
    def __init__(self, api_key: str, model_name: str = "qwen-vl-plus"):
        dashscope.api_key = api_key
        self.model_name = model_name
        self.state = self._load_state()
        self.user_prefs = {
            "likes": ["vegetables", "seafood"],
            "dislikes": ["dairy"],
            "diet": "pescatarian",
        }

    # ----- state persistence ------------------------------------------------
    def _load_state(self):
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
        return DEFAULT_STATE.copy()

    def _save_state(self):
        STATE_FILE.write_text(json.dumps(self.state, indent=2))

    # ----- helpers ----------------------------------------------------------
    @staticmethod
    def _encode_image(path: str | Path) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    # ------------- 顶部导入 -------------


    # ------------- _chat -----------------
    def _chat(self, messages):
        resp = ChatCompletion.create(
            model=self.model_name,
        messages=messages,
        functions=FUNCTION_SIGNATURES,
        function_call="auto",
        )
        return resp

    def _run_tool(self, name: str, kwargs: Dict[str, Any]) -> str:
        if name == "lift":
            return lift(**kwargs)
        if name == "turn":
            return turn(**kwargs)
        if name == "fetch":
            return fetch()
        raise ValueError(f"Unknown tool {name}")

    def _agent_loop(self, messages: List[Dict[str, Any]]) -> str:
        while True:
            raw = self._chat(messages)
            msg = raw["output"]["choices"][0]["message"]

            if "function_call" in msg:
                call = msg["function_call"]
                name = call["name"]
                args = json.loads(call.get("arguments", "{}"))

                result = self._run_tool(name, args)
                messages.append(msg)
                messages.append({"role": "tool", "name": name, "content": result})
                continue

            return msg.get("content", "")

    # ----- high‑level API ---------------------------------------------------
    def _build_system_prompt(self):
        return SYSTEM_TEMPLATE.format(
            state_json=json.dumps(self.state, indent=2),
            prefs_json=json.dumps(self.user_prefs, indent=2),
        )

    def handle_new_item(self, img_path: str | Path):
        b64 = self._encode_image(img_path)
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": "NEW_ITEM", "images": [{"type": "base64", "data": b64}]},
        ]
        answer = self._agent_loop(messages)
        print("\nAssistant:", answer)

    def suggest_item(self):
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": "SUGGEST"},
        ]
        answer = self._agent_loop(messages)
        print("\nAssistant:", answer)

    def tick(self):
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": "TICK"},
        ]
        answer = self._agent_loop(messages)
        print("\nAssistant:", answer)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"#os.getenv("DASHSCOPE_API_KEY")
    if not key:
        print("❌ Please set the DASHSCOPE_API_KEY environment variable.")
        sys.exit(1)

    agent = FridgeAgent(key)

    if len(sys.argv) >= 2:
        agent.handle_new_item(sys.argv[1])
    else:
        agent.tick()
