# 🎹 Profesor Abelton Tutorial - Hrvatski

**Kompletni vodič za apsolutne početnike**

---

## 📚 Sadržaj

1. [Što je Profesor Abelton?](#što-je-profesor-abelton)
2. [Instalacija korak po korak](#instalacija-korak-po-korak)
3. [Prvi koraci](#prvi-koraci)
4. [Osnovne naredbe](#osnovne-naredbe)
5. [Napredne funkcije](#napredne-funkcije)
6. [Učenje produkcije](#učenje-produkcije)
7. [Troubleshooting](#troubleshooting)

---

## Što je Profesor Abelton?

Profesor Abelton je **virtualni asistent** za Ableton Live koji ti omogućuje:

- 🗣️ **Razgovor s DAW-om** - Umjesto klikanja, samo pitaš
- 🎓 **Učenje produkcije** - Postavi bilo koje pitanje
- ⚡ **Brži workflow** - Automatizacija dosadnih zadataka
- 🤖 **Pametne sugestije** - AI zna što radiš i pomaže

### Primjeri:

**Umjesto:**
```
1. Klikni Track > Insert MIDI Track
2. Klikni Device Browser
3. Traži "Wavetable"
4. Drag & drop
5. Itd...
```

**Sada:**
```
"Napravi MIDI traku s Wavetable instrumentom"
✅ Gotovo u sekundi!
```

---

## Instalacija Korak Po Korak

### Korak 1: Provjeri Python

**Imaš li Python instaliran?**

```batch
# Otvori Command Prompt (Win+R, upiši "cmd")
python --version
```

**Vidiš li nešto poput "Python 3.11.0"?**
- ✅ DA - Preskoči na Korak 2
- ❌ NE - Instaliraj Python:

#### Instalacija Pythona (Windows):

1. Idi na: https://www.python.org/downloads/
2. Klikni **"Download Python 3.11"**
3. Pokreni installer
4. ⚠️ **VAŽNO**: Označi **"Add Python to PATH"**
5. Klikni "Install Now"
6. Pričekaj
7. Restartuj kompjuter

### Korak 2: Preuzmi Profesor Abelton

1. Preuzmi **AI-COPILOT-NOVI.zip**
2. Raspakuj u `Downloads` ili negdje gdje će ostati
3. Zapamti lokaciju!

### Korak 3: Pokreni Instalaciju

```batch
1. Otvori folder AI-COPILOT-NOVI
2. Dvaput klikni na: install.bat
3. Pričekaj (može trajati 2-5 minuta)
```

**Što se događa:**
- ⏳ Provjerava Python i pip
- ⏳ Stvara virtualno okruženje
- ⏳ Instalira biblioteke (requests, speech_recognition, itd.)
- ⏳ Kopira script u Ableton folder
- ⏳ Stvara prečace na desktopu

**Na kraju vidiš:**
```
✅ INSTALLATION COMPLETE!

📋 NEXT STEPS:
  1. Open Ableton Live
  2. Go to Preferences > Link/Tempo/MIDI
  ...
```

### Korak 4: Postavi Ableton

```
1. Otvori Ableton Live
2. Otvori Preferences:
   - Windows: Ctrl + ,
   - Mac: Cmd + ,
3. Klikni na tab: Link/Tempo/MIDI
4. U Control Surface dropdown-u:
   - Odaberi "ProfesorAbelton"
5. Input i Output ostavi na "None"
6. Zatvori Preferences
```

**Provjera:**

Idi na **Help > Show Log File**

Trebao bi vidjeti:
```
🚀 Profesor Abelton Remote Script Loading...
📊 Detected Ableton Version: 12+
✅ Profesor Abelton Remote Script Started Successfully!
```

### Korak 5: Instaliraj Ollama (Besplatno!)

**Ne želiš plaćati API ključeve? Koristi Ollama!**

```
1. Idi na: https://ollama.ai/download
2. Preuzmi za Windows
3. Instaliraj (jednostavna instalacija)
4. Otvori Command Prompt
5. Upiši:
   ollama serve
6. U drugom Command Prompt-u:
   ollama pull llama3.1
7. Pričekaj download (3-4 GB)
8. Gotovo!
```

**Alternativa: Cloud AI**

Ako želiš bolje modele (GPT-4, Claude):
- Registriraj se na OpenAI, Anthropic, itd.
- Generiraj API ključ
- Postavi kao environment varijablu
- Vidi README.md za detalje

---

## Prvi Koraci

### 1. Pokreni Server

```
Način 1: Desktop prečac
- Dvaput klikni: "Profesor Abelton Server"

Način 2: Manual
- Otvori folder AI-COPILOT-NOVI
- Dvaput klikni: start_copilot.bat
```

**Trebao bi vidjeti:**
```
========================================
   PROFESOR ABELTON
========================================

[1/3] Checking Python installation... OK
[2/3] Virtual environment activated... OK
[3/3] Dependencies installed... OK

========================================
Starting Profesor Abelton Server...
========================================

🚀 Profesor Abelton Server started on localhost:8766
🤖 Using LLM Provider: OLLAMA
🎤 Voice Recognition: Enabled
```

**Pusti da radi!** Nemoj zatvarati ovaj prozor.

### 2. Otvori Ableton

```
1. Pokreni Ableton Live
2. Otvori novi projekt ili postojeći
3. U Log-u (Help > Show Log File) vidiš:
   ✅ Profesor Abelton Remote Script Started Successfully!
```

### 3. Pokreni GUI

```
Način 1: Desktop prečac
- Dvaput klikni: "Profesor Abelton GUI"

Način 2: Manual
- Otvori folder AI-COPILOT-NOVI
- Dvaput klikni: start_gui.bat
```

**Vidiš:**
```
┌─────────────────────────────────┐
│    🎹 Profesor Abelton          │
├─────────────────────────────────┤
│ Status                          │
│ Server: Connected ✓             │ ← ZELENO!
│ Ableton: Waiting...             │
├─────────────────────────────────┤
│ Chat                            │
│ 💡 Profesor Abelton GUI started...   │
│                                 │
└─────────────────────────────────┘
```

### 4. Tvoj Prvi Command!

U text box na dnu, upiši:

```
Create a new MIDI track
```

Klikni **Send** ili pritisni **Enter**.

**Što se događa:**
1. GUI šalje poruku serveru
2. Server šalje Ollama AI-u
3. AI generira command
4. Server šalje command Abletonu
5. Ableton izvršava command
6. **Nova traka se pojavljuje!** ✨

**U GUI vidiš:**
```
👤 You: Create a new MIDI track
🤖 Ollama: I'll create a MIDI track for you...
✅ Created midi track
```

---

## Osnovne Naredbe

### Kreiranje Traka

```
"Create a new MIDI track"
"Napravi novu MIDI traku"
"Add an audio track"
"Dodaj audio traku"
"Create 3 MIDI tracks"
"Napravi 3 MIDI trake"
```

### Transport Kontrola

```
"Play"
"Pokreni playback"
"Stop"
"Zaustavi"
"Record"
"Snimi"
```

### Tempo

```
"Set tempo to 128"
"Postavi tempo na 128"
"Change BPM to 140"
"Promijeni BPM u 140"
```

### Dodavanje Efekata

```
"Add reverb to track 1"
"Dodaj reverb na traku 1"
"Put a compressor on track 2"
"Stavi kompresor na traku 2"
```

### Volume i Pan

```
"Set track 1 volume to 0.8"
"Postavi glasnoću trake 1 na 0.8"
"Mute track 2"
"Mutiraj traku 2"
"Solo track 1"
"Solo traku 1"
```

### MIDI Clipovi

```
"Create a 4 bar clip in track 1"
"Napravi 4 bar clip u traci 1"
"Add a C major chord to track 1"
"Dodaj C dur akord u traku 1"
```

---

## Napredne Funkcije

### Kompleksne Sekvence

```
"I want to make a techno track. Create:
- 4 MIDI tracks
- Add drums on track 1
- Add a bass on track 2
- Add pads on track 3
- Set tempo to 128"
```

AI će razumjeti i izvršiti sve korake!

### Učenje & Objašnjenja

```
"What is sidechain compression?"
"Što je sidechain kompresija?"

AI: "Sidechain compression je tehnika gdje kompresor na jednom kanalu 
reagira na signal s drugog kanala. Najčešći primjer je 'pumping' efekt 
u dance muzici gdje bas 'duckuje' (smanjuje se) svaki put kad udari kick..."
```

### Troubleshooting

```
"My track is too quiet, what should I do?"
"Moja traka je pretiha, što da radim?"

AI: "Let me help you boost the volume. I'll:
1. Check the master fader
2. Add a Utility device to gain stage
3. Suggest using a limiter..."
```

### Kreativne Ideje

```
"I have a drum loop on track 1. Give me ideas for a melody."

AI: "Great! Based on your drum loop, here are some ideas:
1. Try a minor pentatonic scale melody
2. Add arpeggiated chords
3. Use a call-and-response pattern..."
```

---

## Učenje Produkcije

Profesor Abelton je odličan za učenje! Evo kako:

### Pitaj Što God Želiš

```
"What's the difference between reverb and delay?"
"Koja je razlika između reverba i delaya?"

"How do I make my kick drum punch through the mix?"
"Kako napraviti da kick bubanj probije kroz mix?"

"Explain frequency masking"
"Objasni frequency masking"
```

### Praktične Lekcije

```
"Teach me how to use EQ"
"Nauči me koristiti EQ"

AI: "Great! Let's learn EQ hands-on. I'll:
1. Create a track with an audio loop
2. Add EQ Eight
3. Show you what each band does..."
```

### Žanr-Specifični Savjeti

```
"How do I produce techno?"
"Kako producirati techno?"

"What effects are common in ambient music?"
"Koji efekti su česti u ambient muzici?"
```

---

## 🎤 Glasovne Naredbe

### Setup

1. **Provjeri mikrofon** - Windows Settings > Sound > Input
2. **Otvori GUI**
3. **Odaberi jezik:**
   - Language: **English** ili **Hrvatski**
4. **Klikni 🎤 Voice button**

### Korištenje

**Engleski:**
```
1. Klikni 🎤 Voice (EN)
2. Čekaš "Listening..."
3. Govoriš: "Create a new track"
4. Pričekaš odgovor
```

**Hrvatski:**
```
1. Promijeni Language na: Hrvatski
2. Klikni 🎤 Voice (HR)
3. Čekaš "Listening..."
4. Govoriš: "Napravi novu traku"
```

### Tips za Bolji Recognition:

- 🎤 Govori **jasno** i **sporije**
- 🔇 Smanji pozadinsku buku
- ⏸️ Pravi **pauze** između riječi
- 🔊 Ne govori preglasno ni pretiho
- 🌐 Koristi **jednostavne** rečenice

---

## Troubleshooting

### Server se ne pokreće

**Problem:**
```
❌ ERROR: Python not found!
```

**Rješenje:**
1. Reinstaliraj Python (označi "Add to PATH")
2. Restartuj kompjuter
3. Pokreni install.bat ponovno

---

**Problem:**
```
Port 8766 already in use
```

**Rješenje:**
```batch
# Pronađi proces:
netstat -ano | findstr :8766

# Ubij proces (zamijeni PID):
taskkill /PID 1234 /F

# Ili promijeni port u Config/copilot_config.json
```

### GUI ne spaja se

**Problem:** Status: "Disconnected ✗"

**Rješenje:**
1. Je li Server pokrenut? Vidi "🚀 Server started"
2. Pričekaj 10 sekundi
3. Restartuj GUI
4. Provjeri port u config-u

### Ableton ne vidi Remote Script

**Problem:** Nema "ProfesorAbelton" u Control Surface dropdown-u

**Rješenje:**
1. Provjeri folder:
   ```
   %APPDATA%\Ableton\Live 12\Preferences\User Remote Scripts\ProfesorAbelton
   ```
2. Je li tam __init__.py file?
3. Restartuj Ableton
4. Refresh Preferences

### Voice ne radi

**Problem:** "Voice recognition not available"

**Rješenje:**
```batch
# Instaliraj PyAudio:
pip install pyaudio

# Ako ne radi, preuzmi wheel:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl
```

### Ollama ne reagira

**Problem:** "Cannot connect to Ollama"

**Rješenje:**
```batch
# Provjeri je li pokrenut:
ollama serve

# U drugom terminalu:
ollama list

# Vidiš li "llama3.1"?
# Ne? Preuzmi:
ollama pull llama3.1
```

---

## 💡 Pro Tips

### 1. Koristi Shortcuts

Umjesto klikanja "Send":
- **Enter** - Pošalji poruku
- **Shift+Enter** - Novi red u text box-u

### 2. Chat History

Sve se sprema! Scroll gore da vidiš povijest.

### 3. Multi-step Commands

```
"Do this:
1. Create 2 MIDI tracks
2. Add Wavetable to track 1
3. Add Analog to track 2
4. Set tempo to 128
5. Create 8 bar clips"
```

AI razumije kompleksne zadatke!

### 4. Context-Aware

AI zna što radiš u Abletonu:
```
"Add reverb" ← Na koju traku?
AI: "I'll add reverb to the currently selected track..."
```

### 5. Learn as You Go

```
"Create a compressor on track 1 and explain what each parameter does"
```

---

## 🎯 Što Sada?

Sad kad znaš osnove:

1. **Eksperimentiraj!** - Probaj različite naredbe
2. **Pitaj Svašta** - AI je tu da pomogne
3. **Uči Produkciju** - Postavljaj pitanja
4. **Budi Kreativan** - Koristi AI za inspiraciju

---

## 📚 Dodatni Resursi

- **README.md** - Sva tehnička dokumentacija
- **Config/copilot_config.json** - Sve postavke
- **Docs/** - Dodatni tutoriali

---

## 🎵 Sretno!

Imaš li pitanja? Pitaj Profesor Abelton! 😊

```
"How do I use Profesor Abelton effectively?"
"Kako efikasno koristiti Profesor Abelton?"
```

**Uživaj u produkciji! 🚀🎹**

