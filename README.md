# Zorvael

Kendi bilgisayarında çalışan, Türkçe sesle ya da yazıyla konuşan kişisel yapay zekâ asistanı.

## Neler yapar
- **Çoklu anahtar:** `.env` içine istediğin kadar API anahtarı yazarsın. Biri bitince, limiti dolunca ya da geçersiz çıkınca otomatik sıradakine geçer. Geçici sorunlarda anahtarı kısa süre bekletip geri alır.
- **Hafıza:** Konuşmalar `memory.db` dosyasına kaydedilir. Yeniden açtığında kaldığı yerden devam eder. Senin hakkındaki kalıcı bilgileri (ad, tercih, proje) ayrıca öğrenir; "bunu unut" dersen siler; "geçen gün ... hakkında ne konuşmuştuk" dersen eski konuşmalarda arar.
- **Kod yazma:** Kodu `workspace/` klasörüne dosya olarak yazar, okur, listeler. Komut çalıştırması gerekirse (ör. `python app.py`) her seferinde konsolda onayını ister. Dosya araçları workspace dışına çıkamaz.
- **Telefon (Android):** ADB ile uygulama açar, arama ve SMS hazırlar, ekran görüntüsü alır; hassas işlerde onay ister. Kurulum: `PHONE.md`.
- **Diğer işler:** saat, Google araması, site açma, izinli uygulamaları açma, not alma.

## Kurulum
1. Python 3.10+ kur.
2. Anthropic Console'dan API anahtar(lar)ı al.
3. `.env.example` dosyasını `.env` olarak kopyala, `ZORVAEL_API_KEYS=anahtar1,anahtar2,...` yaz.
4. `pip install -r requirements.txt`
   - Windows'ta PyAudio hata verirse: `pip install pipwin` sonra `pipwin install pyaudio`
   - macOS: önce `brew install portaudio`
   - Linux: önce `sudo apt install portaudio19-dev`
5. Çalıştır:
   - Sesli: `python main.py` ("Zorvael, ..." de)
   - Yazılı (kod işleri için daha rahat): `python main.py --text` (`/anahtarlar` yazarsan anahtarların durumunu görürsün)

## Dosyalar
`main.py` döngü · `brain.py` Claude + araç döngüsü · `keypool.py` anahtar geçişi · `memory.py` hafıza · `voice.py` ses · `tools.py` yetenekler · `phone.py` telefon kontrolü · `config.py` kişilik ve ayarlar

## Güvenlik
- `.env`, `memory.db` ve `workspace/` `.gitignore` içindedir; anahtarlarını asla commit etme.
- Çok sayıda anahtarı yalnızca kendi hesaplarının ya da ekibinin anahtarları için kullan; sağlayıcının kullanım şartlarına uymak sana ait.
- API kullanımı kullandığın kadar ücretlidir.
