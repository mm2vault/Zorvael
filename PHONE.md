# Zorvael + Android telefon

Zorvael telefonuna bilgisayardan, USB ya da Wi-Fi üzerinden ADB ile bağlanır. Telefona uygulama kurmak gerekmez.

## Telefonda (bir kez)
1. Ayarlar → Telefon hakkında → **Yapı numarası**na 7 kez dokun (Geliştirici seçenekleri açılır).
2. Ayarlar → Geliştirici seçenekleri → **USB hata ayıklama**yı aç.
   (Kablosuz için ayrıca **Kablosuz hata ayıklama**yı aç.)

## Bilgisayarda (bir kez)
1. Platform-tools indir: https://developer.android.com/tools/releases/platform-tools
   Zip'i çıkar, klasör yolunu PATH'e ekle ya da `.env` içine `ADB_PATH=C:\platform-tools\adb.exe` yaz.
2. **USB ile:** Telefonu kabloyla bağla, telefonda çıkan "USB hata ayıklamaya izin ver" sorusuna **İzin ver** de. Kontrol: `adb devices` listede telefonu görmelisin.
3. **Kablosuz:** Telefon ve bilgisayar aynı Wi-Fi'da olsun. Kablosuz hata ayıklama → "Eşleştirme koduyla eşle" ekranındaki adres ve kodla:
   `adb pair IP:PORT` (kodu yaz), sonra ana ekrandaki adresle `adb connect IP:PORT`.

## Kullanım
`python main.py --text` açıkken: "telefonun pili kaç", "telefonda youtube'u aç", "Ali'yi ara" (numara ver), "şu numaraya selam diye SMS hazırla".

## İzin sistemi
- Onaysız yapılanlar: durum, uygulama açma, adres açma, ekran görüntüsü, kaydırma, tuşlar, uygulama listesi.
- **Her seferinde senden onay istenenler:** arama, SMS hazırlama, dokunma, yazma. Konsolda `e` yazmazsan yapılmaz.
- SMS'i Zorvael göndermez; yazma ekranını açar, Gönder'e sen basarsın.
- Zorvael'in yetkisini istediğin an geri alabilirsin: telefonda USB hata ayıklamayı kapat ya da Geliştirici seçeneklerinden "USB hata ayıklama yetkilerini iptal et".

## Sınırlar
- Sadece Android. iPhone buna izin vermez.
- ADB ile yazarken Türkçe karakterler (ç ğ ı ö ş ü) yazılamaz.
- WhatsApp gibi uygulamalarda mesajı otomatik gönderme yok, sadece açar. Ekrandaki öğeleri görüp tıklamak için sonraki aşama bir Android uygulaması (erişilebilirlik servisi) olacak.
