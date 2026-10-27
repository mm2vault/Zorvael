"""Android telefon kontrolü (ADB üzerinden). Hassas işlerde her seferinde senden onay ister."""
import datetime
import os
import re
import shlex
import shutil
import subprocess

import config

ADB = os.getenv("ADB_PATH", "adb")
SHOTS = os.path.join(config.WORKSPACE, "screens")

# Tanınan uygulamalar (ad -> paket). Listede olmayan için paket adını doğrudan söyleyebilirsin.
APPS = {
    "whatsapp": "com.whatsapp", "youtube": "com.google.android.youtube", "chrome": "com.android.chrome",
    "instagram": "com.instagram.android", "telegram": "org.telegram.messenger", "spotify": "com.spotify.music",
    "harita": "com.google.android.apps.maps", "ayarlar": "com.android.settings", "kamera": "com.android.camera",
    "tiktok": "com.zhiliaoapp.musically", "gmail": "com.google.android.gm",
}
KEYS = {"ana ekran": "KEYCODE_HOME", "geri": "KEYCODE_BACK", "son uygulamalar": "KEYCODE_APP_SWITCH",
        "sesi aç": "KEYCODE_VOLUME_UP", "sesi kıs": "KEYCODE_VOLUME_DOWN", "sessize al": "KEYCODE_VOLUME_MUTE",
        "oynat/duraklat": "KEYCODE_MEDIA_PLAY_PAUSE", "sonraki şarkı": "KEYCODE_MEDIA_NEXT",
        "önceki şarkı": "KEYCODE_MEDIA_PREVIOUS", "enter": "KEYCODE_ENTER"}


class PhoneError(Exception):
    pass


def _adb(*args, timeout=20, binary=False):
    if not shutil.which(ADB):
        raise PhoneError("adb bulunamadı. PHONE.md dosyasındaki kurulum adımlarını uygula.")
    r = subprocess.run([ADB, *args], capture_output=True, timeout=timeout)
    if r.returncode != 0:
        raise PhoneError((r.stderr or r.stdout).decode(errors="replace").strip() or "adb hatası")
    return r.stdout if binary else r.stdout.decode(errors="replace").strip()


def _shell(*parts, **kw):
    """Cihaz kabuğuna giden her parça tırnaklanır (komut enjeksiyonunu önler)."""
    return _adb("shell", *[shlex.quote(str(p)) for p in parts], **kw)


def _confirm(what):
    print(f"\n[TELEFON ONAYI] Zorvael şunu yapmak istiyor: {what}")
    return input("İzin veriyor musun? [e/h]: ").strip().lower() in ("e", "evet", "y", "yes")


def _guard(fn):
    def wrapper(**kw):
        try:
            return fn(**kw)
        except PhoneError as e:
            return f"Telefon hatası: {e}"
        except subprocess.TimeoutExpired:
            return "Telefon zaman aşımına uğradı."
    return wrapper


def _num(number):
    n = re.sub(r"[\s\-()]", "", number)
    if not re.fullmatch(r"\+?[0-9]{3,15}", n):
        raise PhoneError("Geçersiz telefon numarası.")
    return n


@_guard
def status():
    devs = [l for l in _adb("devices", "-l").splitlines()[1:] if l.strip()]
    if not devs:
        return "Bağlı telefon yok. PHONE.md kurulumunu yap."
    out = _shell("dumpsys", "battery")
    level = re.search(r"level:\s*(\d+)", out)
    charging = re.search(r"status:\s*(\d+)", out)
    return f"Bağlı: {devs[0]} | Pil: %{level.group(1) if level else '?'}" + (" (şarjda)" if charging and charging.group(1) == "2" else "")


@_guard
def open_app(name):
    pkg = APPS.get(name.strip().lower(), name.strip())
    if not re.fullmatch(r"[A-Za-z0-9_.]+", pkg):
        raise PhoneError("Geçersiz uygulama adı.")
    _shell("monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1")
    return f"{name} telefonda açıldı."


@_guard
def open_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    _shell("am", "start", "-a", "android.intent.action.VIEW", "-d", url)
    return f"{url} telefonda açıldı."


@_guard
def call(number):
    n = _num(number)
    if not _confirm(f"{n} numarasını ARAMAK"):
        return "Kullanıcı aramayı reddetti."
    _shell("am", "start", "-a", "android.intent.action.CALL", "-d", f"tel:{n}")
    return f"{n} aranıyor."


@_guard
def sms(number, text):
    n = _num(number)
    if not _confirm(f"{n} numarasına SMS hazırlamak: «{text}»"):
        return "Kullanıcı reddetti."
    _shell("am", "start", "-a", "android.intent.action.SENDTO", "-d", f"sms:{n}", "--es", "sms_body", text)
    return "SMS ekranı açıldı. Göndermek için telefonda Gönder'e bas."


@_guard
def screenshot():
    os.makedirs(SHOTS, exist_ok=True)
    path = os.path.join(SHOTS, datetime.datetime.now().strftime("ekran_%Y%m%d_%H%M%S.png"))
    data = _adb("exec-out", "screencap", "-p", binary=True)
    with open(path, "wb") as f:
        f.write(data)
    return f"Ekran görüntüsü kaydedildi: {path}"


@_guard
def tap(x, y):
    if not _confirm(f"ekranda ({int(x)}, {int(y)}) noktasına DOKUNMAK"):
        return "Kullanıcı reddetti."
    _shell("input", "tap", int(x), int(y))
    return "Dokunuldu."


@_guard
def swipe(x1, y1, x2, y2, ms=300):
    _shell("input", "swipe", int(x1), int(y1), int(x2), int(y2), int(ms))
    return "Kaydırıldı."


@_guard
def type_text(text):
    if not text.isascii():
        raise PhoneError("ADB ile sadece ASCII karakter yazılabiliyor (ç, ğ, ı, ö, ş, ü yazılamaz).")
    if not _confirm(f"telefonda şunu YAZMAK: «{text}»"):
        return "Kullanıcı reddetti."
    _shell("input", "text", text.replace(" ", "%s"))
    return "Yazıldı."


@_guard
def key(name):
    code = KEYS.get(name.strip().lower())
    if not code:
        raise PhoneError("Bilinmeyen tuş. Seçenekler: " + ", ".join(KEYS))
    _shell("input", "keyevent", code)
    return f"{name} tuşuna basıldı."


@_guard
def list_apps():
    out = _shell("pm", "list", "packages", "-3")
    return "\n".join(l.replace("package:", "") for l in out.splitlines())[:3000]


FUNCTIONS = {
    "phone_status": lambda **_: status(), "phone_open_app": lambda name, **_: open_app(name=name),
    "phone_open_url": lambda url, **_: open_url(url=url), "phone_call": lambda number, **_: call(number=number),
    "phone_sms": lambda number, text, **_: sms(number=number, text=text), "phone_screenshot": lambda **_: screenshot(),
    "phone_tap": lambda x, y, **_: tap(x=x, y=y),
    "phone_swipe": lambda x1, y1, x2, y2, ms=300, **_: swipe(x1=x1, y1=y1, x2=x2, y2=y2, ms=ms),
    "phone_type": lambda text, **_: type_text(text=text), "phone_key": lambda name, **_: key(name=name),
    "phone_list_apps": lambda **_: list_apps(),
}


def _s(name, desc, props=None, req=None):
    return {"name": name, "description": desc,
            "input_schema": {"type": "object", "properties": props or {}, "required": req or []}}


_t, _n = {"type": "string"}, {"type": "number"}
SCHEMAS = [
    _s("phone_status", "Telefonun bağlı olup olmadığını ve pil seviyesini söyler."),
    _s("phone_open_app", "Telefonda uygulama açar. Bilinenler: " + ", ".join(APPS) + ". Diğerleri için paket adı.", {"name": _t}, ["name"]),
    _s("phone_open_url", "Telefonda bir web adresi açar.", {"url": _t}, ["url"]),
    _s("phone_call", "Telefondan bir numarayı arar. Kullanıcı onay verir.", {"number": _t}, ["number"]),
    _s("phone_sms", "Telefonda SMS yazma ekranını hazırlar (gönderme tuşuna kullanıcı basar). Onay ister.", {"number": _t, "text": _t}, ["number", "text"]),
    _s("phone_screenshot", "Telefonun ekran görüntüsünü alır ve kaydeder."),
    _s("phone_tap", "Telefon ekranında bir noktaya dokunur (piksel x, y). Onay ister.", {"x": _n, "y": _n}, ["x", "y"]),
    _s("phone_swipe", "Telefon ekranında kaydırır.", {"x1": _n, "y1": _n, "x2": _n, "y2": _n, "ms": _n}, ["x1", "y1", "x2", "y2"]),
    _s("phone_type", "Telefonda açık olan alana ASCII metin yazar. Onay ister.", {"text": _t}, ["text"]),
    _s("phone_key", "Telefonda bir tuşa basar: " + ", ".join(KEYS), {"name": _t}, ["name"]),
    _s("phone_list_apps", "Telefondaki kullanıcı uygulamalarının paket adlarını listeler."),
]
