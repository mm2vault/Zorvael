import os
from dotenv import load_dotenv

load_dotenv()


def _collect_keys():
    """API anahtarlarını toplar. Üç yol da desteklenir ve birleştirilir:
    ZORVAEL_API_KEYS=a,b,c   |   ANTHROPIC_API_KEY=a   |   ANTHROPIC_API_KEY_1=a, ANTHROPIC_API_KEY_2=b ...
    """
    keys = []
    keys += [k.strip() for k in os.getenv("ZORVAEL_API_KEYS", "").replace("\n", ",").split(",")]
    keys.append(os.getenv("ANTHROPIC_API_KEY", "").strip())
    for i in range(1, 51):
        keys.append(os.getenv(f"ANTHROPIC_API_KEY_{i}", "").strip())
    seen, out = set(), []
    for k in keys:
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


API_KEYS = _collect_keys()
BRAIN = os.getenv("ZORVAEL_BRAIN", "claude").lower()   # claude | ollama
MODEL = os.getenv("ZORVAEL_MODEL", "claude-sonnet-5-5")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("ZORVAEL_OLLAMA_MODEL", "qwen2.5:7b")
VOICE = os.getenv("ZORVAEL_VOICE", "tr-TR-AhmetNeural")
WAKE = os.getenv("ZORVAEL_WAKE", "zorvael").lower()
BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("ZORVAEL_DB", os.path.join(BASE, "memory.db"))
WORKSPACE = os.getenv("ZORVAEL_WORKSPACE", os.path.join(BASE, "workspace"))
RECALL_TURNS = int(os.getenv("ZORVAEL_RECALL_TURNS", "20"))

WAKE_VARIANTS = {WAKE, "zorvel", "zorveyl", "zorval", "zorvayel", "zor wael", "zor vael"}

PERSONA = (
    "Sen Zorvael'sin: kullanıcıya özel, sadık ve zeki bir kişisel yapay zekâ asistanısın. "
    "Türkçe konuşursun, sakin ve kendinden emin bir tonun var, ara sıra ince bir espri yaparsın. "
    "Normal sohbette cevapların kısa ve net olsun; madde işareti ve emoji kullanma. "
    "Hafızan var: kullanıcı hakkında kalıcı bir şey öğrenirsen (adı, tercihleri, projeleri, planları) "
    "remember aracıyla kaydet. Eski bir konuşmayı sorarsa search_memory ile ara. "
    "Kod yazman istenirse kodu write_file ile workspace klasörüne dosya olarak yaz, sesli cevapta sadece ne yaptığını kısaca anlat; "
    "kodu yüksek sesle okuma. Dosyayı çalıştırmak veya komut koşmak için run_command kullan (kullanıcı onay verir). "
    "Telefon araçların var (phone_*): kullanıcının Android telefonunda uygulama açabilir, arama ve SMS hazırlayabilir, ekran görüntüsü alabilirsin; arama, SMS, dokunma ve yazma işlerini kullanıcı onaylar. Onay istenirse bunu kullanıcıya kısaca söyle. Bilgisayarda iş yapmak için diğer araçlarını kullan. Emin olmadığın şeyi uydurma, bilmediğini söyle."
)
