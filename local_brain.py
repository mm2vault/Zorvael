"""Ücretsiz yerel beyin: Ollama üzerinde çalışan açık kaynak model. İnternet ve API ücreti gerekmez."""
import json
import types
import urllib.error
import urllib.request

import config
from brain import build_system
from tools import SCHEMAS, run_tool


def _ollama_tools():
    return [{"type": "function", "function": {"name": s["name"], "description": s["description"],
                                              "parameters": s["input_schema"]}} for s in SCHEMAS]


class OllamaBrain:
    def __init__(self, memory):
        self.memory = memory
        self.history = memory.recent_messages(config.RECALL_TURNS)
        label = f"ollama:{config.OLLAMA_MODEL}"
        # main.py'nin anahtar durumu göstermesi için uyumluluk
        self.pool = types.SimpleNamespace(keys=[label], status=lambda: [(label, "yerel model")])

    def reset(self):
        self.history = []

    def _chat(self, messages):
        body = json.dumps({"model": config.OLLAMA_MODEL, "messages": messages, "tools": _ollama_tools(),
                           "stream": False}).encode()
        req = urllib.request.Request(config.OLLAMA_HOST + "/api/chat", data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)["message"]
        except urllib.error.URLError as e:
            raise RuntimeError(f"Ollama'ya ulaşılamadı ({config.OLLAMA_HOST}). Ollama açık mı ve "
                               f"`ollama pull {config.OLLAMA_MODEL}` yapıldı mı? ({e})")

    def ask(self, text):
        self.history.append({"role": "user", "content": text})
        self.history = self.history[-40:]
        while self.history and self.history[0]["role"] != "user":
            self.history.pop(0)
        self.memory.add_message("user", text)
        for _ in range(8):  # araç döngüsü sınırı
            msg = self._chat([{"role": "system", "content": build_system(self.memory)}] + self.history)
            self.history.append(msg)
            calls = msg.get("tool_calls") or []
            if not calls:
                answer = (msg.get("content") or "").strip()
                self.memory.add_message("assistant", answer)
                return answer
            for c in calls:
                fn = c["function"]
                args = fn.get("arguments") or {}
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except ValueError:
                        args = {}
                print(f"  [araç] {fn['name']} {str(args)[:120]}")
                self.history.append({"role": "tool", "tool_name": fn["name"], "content": run_tool(fn["name"], args)})
        return "Bu işi bitiremedim, çok fazla adım gerekti."
