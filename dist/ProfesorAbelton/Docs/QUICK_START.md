# 🚀 Quick Start Guide - Profesor Abelton

**Za apsolutne početnike - 5 minuta do prvog AI razgovora!**

---

## Windows Korisnici

### 1. Instalacija (2 minute)

```
1. Dvaput klikni na:  install.bat
2. Pričekaj da se sve instalira
3. Gotovo!
```

### 2. Pokretanje (1 minuta)

```
1. Dvaput klikni: "Profesor Abelton Server" (na desktopu)
2. Pričekaj da vidiš: "🚀 Profesor Abelton Server started"
3. Pusti ga da radi u pozadini
```

### 3. Otvori Ableton (1 minuta)

```
1. Otvori Ableton Live
2. Idi na: Preferences (Ctrl+,)
3. Tab: Link/Tempo/MIDI
4. Control Surface: Odaberi "ProfesorAbelton"
5. Zatvori preferences
```

### 4. Otvori GUI (30 sekundi)

```
1. Dvaput klikni: "Profesor Abelton GUI" (na desktopu)
2. Trebao bi vidjeti zelenu "Connected ✓" oznaku
```

### 5. Probaj! (30 sekundi)

```
Upiši u text box:

"Create a new MIDI track"

Ili:

"Napravi novu MIDI traku"

Klikni Send!
```

---

## Mac Korisnici

### 1. Instalacija

```bash
# Otvori Terminal (Cmd+Space, upiši "Terminal")
cd Downloads/AI-COPILOT-NOVI
chmod +x install.sh
./install.sh
```

### 2. Pokretanje

```bash
./start_copilot.sh
# Pusti da radi u pozadini
```

### 3. Otvori Ableton

```
1. Otvori Ableton Live
2. Preferences (Cmd+,)
3. Link/Tempo/MIDI
4. Control Surface: "ProfesorAbelton"
```

### 4. Otvori GUI

```bash
# U novom Terminal prozoru:
./start_gui.sh
```

### 5. Probaj!

Upiši: `"Create a new MIDI track"`

---

## Linux Korisnici

### 1. Instalacija

```bash
cd AI-COPILOT-NOVI
chmod +x install.sh
./install.sh
```

### 2. Pokretanje

```bash
./start_copilot.sh &
```

### 3. Ableton Setup

```
Preferences > Link/Tempo/MIDI > Control Surface: "ProfesorAbelton"
```

### 4. GUI

```bash
./start_gui.sh
```

---

## 🎤 Glasovne Naredbe

### Engleski:

1. Klikni **🎤 Voice (EN)**
2. Govori: *"Create a new track"*
3. Pričekaj odgovor

### Hrvatski:

1. Promjeni Language na: **Hrvatski**
2. Klikni **🎤 Voice (HR)**
3. Govori: *"Napravi novu traku"*

---

## 🆓 Koristi BESPLATNO s Ollama

Ne želiš plaćati API ključeve? Koristi Ollama!

### Windows:

```
1. Preuzmi Ollama: https://ollama.ai/download
2. Instaliraj
3. Otvori Command Prompt i upiši:
   ollama serve
4. U drugom prozoru:
   ollama pull llama3.1
5. Gotovo! Profesor Abelton će automatski koristiti Ollama
```

### Mac/Linux:

```bash
# Instaliraj Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pokreni server
ollama serve &

# Preuzmi model
ollama pull llama3.1
```

---

## ✅ Provjeri Radi Li

### Server check:

Trebao bi vidjeti:
```
🚀 Profesor Abelton Server started on localhost:8766
🤖 Using LLM Provider: OLLAMA
🎤 Voice Recognition: Enabled
```

### GUI check:

- **Status**: "Connected ✓" (zeleno)
- **Ableton**: "Waiting..." ili ima info o trakama

### Ableton check:

U Ableton Log-u (Help > Show Log File) trebao bi vidjeti:
```
🚀 Profesor Abelton Remote Script Loading...
✅ Profesor Abelton Remote Script Started Successfully!
```

---

## 💬 Prvi Razgovor

### Za Početnike:

```
"I'm a complete beginner. Help me create my first track."
```

### Za Učenje:

```
"What is a compressor and how do I use it?"
"Što je EQ i kako ga koristiti?"
```

### Za Kreiranje:

```
"Create a techno drum pattern"
"Add a reverb to track 1"
"Set tempo to 128 BPM"
```

---

## ❓ Problemi?

### Server se ne pokreće?

```bash
# Provjeri Python:
python --version

# Reinstaliraj:
install.bat  (ili ./install.sh)
```

### GUI kaže "Disconnected"?

```
1. Je li Server pokrenut?
2. Vidi li se Terminal s "Server started"?
3. Pričekaj 5 sekundi i refresh
```

### Ableton ne vidi script?

```
1. Restartuj Ableton
2. Provjeri Preferences > Control Surface
3. Ako nije tu, ručno kopiraj RemoteScript folder
```

### Voice ne radi?

```bash
# Instaliraj PyAudio:
pip install pyaudio

# Mac dodatno:
brew install portaudio
```

---

## 🎓 Sljedeći Koraci

1. **Pročitaj README.md** - Detaljne upute
2. **Eksperimentiraj** - Pitaj AI bilo što!
3. **Dodaj API ključeve** - Za naprednije modele (opciono)
4. **Pridruži se community-ju** - Za pomoć i savjete

---

## 🎵 Primjeri Što Možeš Pitati

### Kreiranje:
- "Create 3 MIDI tracks"
- "Add a reverb and delay to track 1"
- "Make a 4 bar clip with C major chord"

### Učenje:
- "Explain sidechaining"
- "What's the difference between delay and reverb?"
- "How do I make my mix louder?"

### Na Hrvatskom:
- "Napravi novu audio traku"
- "Objasni što je kompresor"
- "Kako napraviti dobar mix?"

---

## 🏆 Gotovo!

Sada imaš:
- ✅ AI asistenta u Ableton-u
- ✅ Text i voice kontrolu
- ✅ Neograničene mogućnosti učenja
- ✅ Potpuno funkcionalan setup

**Uživaj u pravljenju muzike! 🎹🚀**

---

*Dodatna pomoć? Pogledaj README.md ili kontaktiraj podršku.*

