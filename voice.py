"""Kulak ve ağız: mikrofon -> metin, metin -> ses."""
import asyncio
import os
import tempfile

import edge_tts
import pygame
import speech_recognition as sr

import config

_rec = sr.Recognizer()
_rec.pause_threshold = 0.9
pygame.mixer.init()


def calibrate(mic):
    print("Ortam sesi ölçülüyor, bir saniye sessiz kal...")
    _rec.adjust_for_ambient_noise(mic, duration=1)


def listen(mic, timeout=None, phrase_limit=15) -> str:
    """Bir cümle dinler, Türkçe metne çevirir. Anlaşılmazsa boş döner."""
    try:
        audio = _rec.listen(mic, timeout=timeout, phrase_time_limit=phrase_limit)
    except sr.WaitTimeoutError:
        return ""
    try:
        return _rec.recognize_google(audio, language="tr-TR").strip()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print("Ses tanıma servisine ulaşılamadı:", e)
        return ""


async def _synth(text: str, path: str):
    await edge_tts.Communicate(text, config.VOICE).save(path)


def speak(text: str):
    if not text:
        return
    print("Zorvael:", text)
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        asyncio.run(_synth(text, path))
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        pygame.mixer.music.unload()
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
