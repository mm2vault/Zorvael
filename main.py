"""Zorvael. Sesli mod: 'Zorvael' de, komutunu söyle.  Yazılı mod: python main.py --text"""
import sys

import config
import tools
from brain import Brain
from memory import Memory

EXIT_WORDS = ("kapan", "görüşürüz", "güle güle", "uyu")
RESET_WORDS = ("sohbeti sıfırla", "baştan başla")


def strip_wake(text):
    low = text.lower()
    for w in sorted(config.WAKE_VARIANTS, key=len, reverse=True):
        i = low.find(w)
        if i != -1:
            return text[i + len(w):].strip(" ,.!?")
    return None


def make_brain():
    memory = Memory(config.DB_PATH)
    tools.set_memory(memory)
    if config.BRAIN == "ollama":
        from local_brain import OllamaBrain
        return OllamaBrain(memory), memory
    return Brain(memory), memory


def run_text():
    brain, _ = make_brain()
    print(f"Zorvael yazılı mod ({len(brain.pool.keys)} anahtar, {len(brain.history)} eski mesaj yüklendi). Çıkmak için 'çık'.\n")
    while True:
        try:
            line = input("Sen: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line.lower() in ("çık", "cik", "exit"):
            break
        if line.lower() == "/anahtarlar":
            for a, b in brain.pool.status():
                print(f"  {a}: {b}")
            continue
        try:
            print("Zorvael:", brain.ask(line), "\n")
        except Exception as e:  # noqa: BLE001
            print("Hata:", e)


def run_voice():
    import speech_recognition as sr
    import voice
    brain, _ = make_brain()
    with sr.Microphone() as mic:
        voice.calibrate(mic)
        voice.speak("Zorvael çevrimiçi. Kaldığımız yerden devam edelim.")
        print(f"\n{len(brain.pool.keys)} anahtar, {len(brain.history)} eski mesaj yüklendi. '{config.WAKE}' de. Kapatmak için Ctrl+C.\n")
        while True:
            heard = voice.listen(mic, timeout=None, phrase_limit=12)
            if not heard:
                continue
            print("Duyulan:", heard)
            command = strip_wake(heard)
            if command is None:
                continue
            if not command:
                voice.speak("Evet?")
                command = voice.listen(mic, timeout=6, phrase_limit=15)
                if not command:
                    continue
            low = command.lower()
            if any(w in low for w in EXIT_WORDS):
                voice.speak("Görüşürüz.")
                break
            if any(w in low for w in RESET_WORDS):
                brain.reset()
                voice.speak("Konuşmayı sıfırladım. Uzun vadeli hafızam duruyor.")
                continue
            try:
                voice.speak(brain.ask(command))
            except Exception as e:  # noqa: BLE001
                print("Hata:", e)
                voice.speak("Bir sorun çıktı, tekrar dener misin?")


if __name__ == "__main__":
    try:
        run_text() if "--text" in sys.argv else run_voice()
    except KeyboardInterrupt:
        print("\nKapatıldı.")
