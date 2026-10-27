"""Zorvael'in beyni: anahtar havuzu + hafıza + araç kullanımı."""
import datetime

import config
from keypool import KeyPool
from tools import SCHEMAS, run_tool


def build_system(memory):
    facts = memory.facts()
    mem = "\n".join(f"- {f}" for f in facts) if facts else "(henüz bir şey kaydedilmedi)"
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    return f"{config.PERSONA}\n\nŞu an: {now}\n\nKullanıcı hakkında bildiklerin:\n{mem}"


def _is_user_text(m):
    return m["role"] == "user" and isinstance(m["content"], str)


class Brain:
    def __init__(self, memory):
        self.memory = memory
        self.pool = KeyPool(config.API_KEYS)
        # Önceki konuşmaları geri yükle: Zorvael kaldığı yerden devam eder.
        self.history = memory.recent_messages(config.RECALL_TURNS)

    def reset(self):
        self.history = []

    def _system(self):
        return build_system(self.memory)

    def _trim(self):
        """Geçmişi kısaltır, ama araç çağrısı/sonucu çiftlerini bölmez."""
        if len(self.history) <= 40:
            return
        start = len(self.history) - 40
        while start < len(self.history) and not _is_user_text(self.history[start]):
            start += 1
        self.history = self.history[start:]

    def ask(self, text):
        self.history.append({"role": "user", "content": text})
        self._trim()
        self.memory.add_message("user", text)
        while True:
            resp = self.pool.call(model=config.MODEL, max_tokens=4000, system=self._system(),
                                  tools=SCHEMAS, messages=self.history)
            self.history.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                answer = "".join(b.text for b in resp.content if b.type == "text").strip()
                self.memory.add_message("assistant", answer)
                return answer
            results = []
            for block in resp.content:
                if block.type == "tool_use":
                    print(f"  [araç] {block.name} {str(block.input)[:120]}")
                    results.append({"type": "tool_result", "tool_use_id": block.id,
                                    "content": run_tool(block.name, block.input)})
            self.history.append({"role": "user", "content": results})
