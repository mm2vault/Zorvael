"""Birden fazla API anahtarı arasında otomatik geçiş.
Bir anahtarın kredisi biter, limiti dolar ya da geçersiz çıkarsa sıradakine geçer; geçici sorunlarda bir süre bekletir."""
import time

import anthropic

HOUR = 3600


class KeyPool:
    def __init__(self, keys, verbose=True):
        if not keys:
            raise SystemExit("Hiç API anahtarı yok. .env dosyasına ZORVAEL_API_KEYS=anahtar1,anahtar2,... yaz.")
        self.keys = list(keys)
        self.clients = [anthropic.Anthropic(api_key=k, max_retries=0) for k in self.keys]
        self.blocked_until = [0.0] * len(self.keys)
        self.reason = [""] * len(self.keys)
        self.current = 0
        self.verbose = verbose

    def label(self, i):
        return f"anahtar #{i + 1} (…{self.keys[i][-4:]})"

    def _block(self, i, seconds, why):
        self.blocked_until[i] = time.time() + seconds
        self.reason[i] = why
        if self.verbose:
            print(f"  [anahtar] {self.label(i)} devre dışı: {why}")

    def status(self):
        now = time.time()
        return [(self.label(i), "hazır" if now >= self.blocked_until[i] else self.reason[i]) for i in range(len(self.keys))]

    def call(self, **kwargs):
        n = len(self.keys)
        for step in range(n):
            i = (self.current + step) % n
            if time.time() < self.blocked_until[i]:
                continue
            try:
                resp = self.clients[i].messages.create(**kwargs)
                if i != self.current and self.verbose:
                    print(f"  [anahtar] {self.label(i)} kullanılıyor")
                self.current = i
                return resp
            except anthropic.RateLimitError as e:
                wait = 60
                try:
                    wait = int(float(e.response.headers.get("retry-after", 60)))
                except Exception:  # noqa: BLE001
                    pass
                self._block(i, max(wait, 5), "hız limiti")
            except (anthropic.AuthenticationError, anthropic.PermissionDeniedError):
                self._block(i, 24 * HOUR, "geçersiz ya da yetkisiz anahtar")
            except anthropic.APIStatusError as e:
                text = str(e).lower()
                if e.status_code == 400 and ("credit" in text or "billing" in text):
                    self._block(i, 6 * HOUR, "kredi bitti")
                elif e.status_code in (429, 500, 502, 503, 529):
                    self._block(i, 30, f"sunucu yoğun ({e.status_code})")
                else:
                    raise
            except anthropic.APIConnectionError:
                self._block(i, 10, "bağlantı hatası")
        raise RuntimeError("Tüm API anahtarları şu an kullanılamıyor: " + "; ".join(f"{a}: {b}" for a, b in self.status()))
