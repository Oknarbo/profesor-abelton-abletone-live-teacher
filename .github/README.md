# Profesor Abelton

**"The friend who actually knows Ableton — and is always there to teach you."**

Standalone desktop AI aplikacija koja pretvara prirodni jezik u stvarne akcije unutar Ableton Livea.  
Djeluje kao pametni učitelj i pratitelj — objašnjava, pokazuje i radi stvari umjesto tebe, sve lokalno i u kontekstu tvog trenutnog projekta.

**Verzija:** v2.0.1  
**Platforme:** Windows 10/11 + macOS 12+  
**Ableton Live:** 11 i 12 (Live 10 nije podržan)

---

### 🚀 Zašto postoji Profesor Abelton?

Ableton ima strmu krivulju učenja. Većina ljudi se zaglavi jer tutoriali su predugi, forumi su zbunjujući, a nemaju uvijek pri ruci prijatelja koji zna Ableton.

Profesor Abelton je taj prijatelj — uvijek dostupan, strpljiv i točno zna što se događa u tvom projektu.

---

### Glavne značajke

- **Konverzacijsko učenje** — pitaj bilo što na hrvatskom ili engleskom ("Zašto mi je mix mutan?", "Objasni sidechain", "Postavi osnovnu house strukturu")
- **Potpuna svijest o sesiji** — AI uvijek vidi trackove, tempo, clipove, uređaje i routing
- **35 strukturiranih Claude MCP alata** + Groq kao brzi fallback
- **Multi-command batching** — jedna poruka može izvršiti i do 12 akcija odjednom
- **First Launch Wizard** — automatski instalira Remote Script, postavlja API ključeve i aktivira licencu
- **Sigurnost na prvom mjestu** — sve radi lokalno (loopback), komande su allowlistane, ključevi su šifrirani

---

### Kako radi?

1. GUI šalje poruku lokalnom serveru (`127.0.0.1:8766`)
2. Server analizira sesiju preko **Control Surface Remote Scripta**
3. AI (Claude ili Groq) vraća strukturirane tool-calls
4. Server izvršava akcije direktno u Abletonu

Sve komunikacije su lokalne — nema clouda, nema vanjskih plugina.

---

### Podržane akcije (40 ukupno)

- Kreiranje i upravljanje trackovima (MIDI, Audio, Return)
- Mixer & routing (volume, pan, sendovi, mute, solo…)
- Clipovi i MIDI (kreiranje, noteovi, quantize, humanize, drum patterni…)
- Uređaji i efekti (dodavanje, parametri, presetovi…)
- Transport i session (play, record, tempo, export…)

Puni popis akcija nalazi se u `docs/supported_actions.md` (ili u PDF dokumentaciji).

---

### Kako pokrenuti lokalno (development)

```bash
# 1. Kloniraj repozitorij
git clone https://github.com/tvoje-korisnicko-ime/profesor-abelton.git

# 2. Uđi u folder
cd profesor-abelton

# 3. Instaliraj dependencies (Python)
pip install -r requirements.txt

# 4. Pokreni aplikaciju
python run.py
