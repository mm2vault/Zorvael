"""Zorvael'in yapabildiği işler. Yeni yetenek eklemek için fonksiyon + şema ekle."""
import datetime
import os
import subprocess
import sys
import urllib.parse
import webbrowser

import config

os.makedirs(config.WORKSPACE, exist_ok=True)
NOTES_FILE = os.path.join(config.BASE, "notlar.txt")
MEMORY = None  # main.py doldurur


def set_memory(m):
    global MEMORY
    MEMORY = m


if sys.platform.startswith("win"):
    APPS = {"hesap makinesi": "calc", "not defteri": "notepad", "dosya gezgini": "explorer"}
elif sys.platform == "darwin":
    APPS = {"hesap makinesi": "Calculator", "notlar": "Notes", "müzik": "Music"}
else:
    APPS = {"hesap makinesi": "gnome-calculator", "dosya gezgini": "nautilus"}


def _safe_path(rel):
    """Yalnızca workspace klasörünün içine izin verir."""
    root = os.path.realpath(config.WORKSPACE)
    full = os.path.realpath(os.path.join(root, rel))
    if full != root and not full.startswith(root + os.sep):
        raise ValueError("Sadece workspace klasöründe çalışabilirim.")
    return full


def get_time():
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M, %A")


def open_website(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"{url} açıldı."


def search_web(query):
    webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote(query))
    return f"'{query}' için arama açıldı."


def open_app(name):
    key = name.strip().lower()
    if key not in APPS:
        return f"'{name}' izinli listede yok. Liste: {', '.join(APPS)}."
    target = APPS[key]
    if sys.platform.startswith("win"):
        subprocess.Popen(target, shell=True)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-a", target])
    else:
        subprocess.Popen([target])
    return f"{name} açıldı."


def take_note(text):
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now():%d.%m.%Y %H:%M}] {text}\n")
    return "Not kaydedildi."


def remember(fact):
    return "Hafızaya kaydedildi." if MEMORY.remember(fact) else "Bunu zaten biliyordum."


def forget(text):
    n = MEMORY.forget(text)
    return f"{n} bilgi silindi." if n else "Eşleşen bilgi bulunamadı."


def search_memory(query):
    hits = MEMORY.search(query)
    return "\n".join(hits) if hits else "Eski konuşmalarda bulunamadı."


def write_file(path, content):
    full = _safe_path(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return f"{path} yazıldı ({len(content)} karakter)."


def read_file(path):
    with open(_safe_path(path), encoding="utf-8", errors="replace") as f:
        return f.read()[:8000]


def list_files(path="."):
    full = _safe_path(path)
    return "\n".join(sorted(os.listdir(full))) or "(boş)"


def run_command(command):
    """Workspace içinde komut çalıştırır. Her seferinde konsoldan onay ister."""
    print(f"\n[ONAY] Zorvael şu komutu çalıştırmak istiyor (klasör: {config.WORKSPACE}):\n  {command}")
    if input("Çalıştırılsın mı? [e/h]: ").strip().lower() not in ("e", "evet", "y", "yes"):
        return "Kullanıcı komutu reddetti."
    try:
        r = subprocess.run(command, shell=True, cwd=config.WORKSPACE, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return "Komut 60 saniyede bitmedi, durduruldu."
    out = (r.stdout + r.stderr).strip()
    return f"çıkış kodu {r.returncode}\n{out[:3000]}"


FUNCTIONS = {
    "get_time": lambda **_: get_time(),
    "open_website": lambda url, **_: open_website(url),
    "search_web": lambda query, **_: search_web(query),
    "open_app": lambda name, **_: open_app(name),
    "take_note": lambda text, **_: take_note(text),
    "remember": lambda fact, **_: remember(fact),
    "forget": lambda text, **_: forget(text),
    "search_memory": lambda query, **_: search_memory(query),
    "write_file": lambda path, content, **_: write_file(path, content),
    "read_file": lambda path, **_: read_file(path),
    "list_files": lambda path=".", **_: list_files(path),
    "run_command": lambda command, **_: run_command(command),
}


def _s(name, desc, props=None, req=None):
    return {"name": name, "description": desc,
            "input_schema": {"type": "object", "properties": props or {}, "required": req or []}}


_str = {"type": "string"}
SCHEMAS = [
    _s("get_time", "Şu anki tarih ve saati söyler."),
    _s("open_website", "Bir web sitesini tarayıcıda açar.", {"url": _str}, ["url"]),
    _s("search_web", "Google'da arama yapar.", {"query": _str}, ["query"]),
    _s("open_app", "İzinli listedeki bir uygulamayı açar: " + ", ".join(APPS), {"name": _str}, ["name"]),
    _s("take_note", "Kısa bir notu not dosyasına ekler.", {"text": _str}, ["text"]),
    _s("remember", "Kullanıcı hakkında kalıcı bir bilgiyi uzun vadeli hafızaya kaydeder (kısa, tek cümle).", {"fact": _str}, ["fact"]),
    _s("forget", "Hafızadan, verilen metni içeren bilgileri siler.", {"text": _str}, ["text"]),
    _s("search_memory", "Eski konuşmalarda kelime arar.", {"query": _str}, ["query"]),
    _s("write_file", "workspace klasörüne dosya yazar (kod, metin). Yol göreli olmalı.", {"path": _str, "content": _str}, ["path", "content"]),
    _s("read_file", "workspace içindeki bir dosyayı okur.", {"path": _str}, ["path"]),
    _s("list_files", "workspace içindeki dosyaları listeler.", {"path": _str}),
    _s("run_command", "workspace klasöründe terminal komutu çalıştırır (ör. python app.py). Kullanıcı onay verir.", {"command": _str}, ["command"]),
]


def run_tool(name, args):
    fn = FUNCTIONS.get(name)
    if not fn:
        return f"Bilinmeyen araç: {name}"
    try:
        return str(fn(**args))
    except Exception as e:  # noqa: BLE001
        return f"Araç hatası: {e}"


# Telefon yetenekleri (ADB). phone.py ayrı dosyada, onay mantığı orada.
import phone  # noqa: E402

FUNCTIONS.update(phone.FUNCTIONS)
SCHEMAS.extend(phone.SCHEMAS)
