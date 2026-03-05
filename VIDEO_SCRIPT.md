## VIDEO_SCRIPT — Profesor Abelton (v2.0.0)

### Video meta
- **Cilj**: korisnik u 5 minuta dođe do “radi” (Ableton + Control Surface + prvi command)
- **Trajanje**: ~5:30
- **Platforma**: Windows 10/11 + Ableton Live 12
- **Kanonska imena**:
  - **Product name**: Profesor Abelton
  - **Ableton Control Surface / Remote Script**: `ProfesorAbelton`
- **AI provideri u UI (testirano)**: **GROQ** + **CLAUDE (MCP)**

### Priprema prije snimanja (checklist)
- [ ] Folder: `PROFESOR_ABELTON_CLEAN` na Desktopu ili Downloads
- [ ] Ableton zatvoren (za install/update Remote Script)
- [ ] Groq API key i/ili Claude API key spremni (maskiraj na videu)
- [ ] Rezolucija snimanja: 1920×1080, scaling 100–125%
- [ ] Otvoren Ableton Preferences path (da znaš gdje je Control Surface)

---

## Timeline / shot-by-shot

### 0:00–0:20 — Hook (što je to)
- **Screen**: naslov + GUI kratko
- **Voiceover**: “Profesor Abelton je AI asistent za Ableton. U ovom videu: instalacija, setup Control Surface i prvi command.”

### 0:20–0:55 — Pokretanje launchera
- **Screen**: `PROFESOR_ABELTON_CLEAN` folder
- **Action**: double click `start_all.bat` ili `launch_profesor_abelton.py`
- **Voiceover**: “Launcher pokreće server i GUI.”
- **Expected**: server prozor kaže “Profesor Abelton Server started …”, GUI se otvori

### 0:55–2:10 — First Launch Wizard (install Remote Script)
- **Screen**: wizard
- **Action**:
  - Step Detect: pokaži “Control Surface name: `ProfesorAbelton`”
  - Step Install: klik “Install / Update” → “✅ Installed”
  - Step API Keys: unesi Groq (i/ili Claude) → Save keys
  - Finish
- **Voiceover**:
  - “Ovo kopira Remote Script u Ableton user remote scripts.”
  - “Važno: Control Surface se zove `ProfesorAbelton`.”
- **Expected**: wizard završi bez errora

### 2:10–3:00 — Ableton setup (Control Surface)
- **Screen**: Ableton Preferences → Link/Tempo/MIDI
- **Action**: Control Surface dropdown → odaberi `ProfesorAbelton`, Input/Output None
- **Voiceover**: “Ako ovo ne odabereš, Ableton neće pričati sa serverom.”
- **Expected**: u Ableton Log-u vidiš da se Remote Script učitao (ako pokazuješ log)

### 3:00–4:40 — Demo: 3 komande
- **Screen**: GUI chat
- **Action** (upiši i pošalji):
  1. “postavi novu midi traku”
  2. “postavi tempo na 128”
  3. “dodaj reverb na traku 1”
- **Voiceover**: “Ovo su tri najbrža testa da znaš da sve radi.”
- **Expected**: nova traka + tempo + device (ovisno o Abletonu/device availability)

### 4:40–5:15 — Troubleshooting (2 najčešća)
- **Screen**: kratak checklist u videu (tekst overlay)
- **Problem 1**: “Ne vidim `ProfesorAbelton` u Control Surface”
  - **Fix**: provjeri da folder postoji u “User Remote Scripts”, restart Ableton
- **Problem 2**: “GUI Disconnected”
  - **Fix**: server mora biti up, port 8766, firewall

### 5:15–5:30 — Outro
- **Voiceover**: “Ako želiš nove funkcije, javi na Discord. Sljedeći updateovi dolaze nakon testiranja.”

