# Profesor Abelton

**"The friend who actually knows Ableton — and is always there to teach you."**

A standalone desktop AI application that turns natural language into real Ableton Live actions.  
It acts as an intelligent teacher and companion — explaining concepts, demonstrating techniques, and performing tasks in the context of your current project.

**Version:** v2.0.1  
**Platforms:** Windows 10/11 • macOS 12+  
**Ableton Live:** 11 & 12 (Live 10 not supported)

---

### Why Profesor Abelton Exists

Learning Ableton is hard. Most beginners get stuck not because they lack talent, but because the learning curve is steep and most resources feel cold, slow or abstract.

Profesor Abelton is that one friend who always picks up the phone at midnight — patient, clear, and never makes you feel dumb for asking.

It is **not** just another macro tool or automation script.  
Its primary goal is **guided learning through conversation**.

---

### Key Features

- **Conversational Learning** — Ask anything in plain English (or Croatian). The AI explains in context and at your level.
- **Live Session Awareness** — The AI always knows your current project (tracks, clips, devices, tempo, routing…).
- **35 Structured Claude MCP Tools** — Reliable, schema-validated actions (no text parsing guesswork).
- **Groq Fast Fallback** — Ultra-fast responses using llama-3.3-70b when speed matters.
- **Multi-Command Batching** — One message can trigger up to 12 actions at once.
- **First Launch Wizard** — Automatically installs the Remote Script, sets up API keys and activates the license.
- **Strong Security** — Loopback-only, command allowlist (40 actions), encrypted keys, parameter sanitization, machine-bound license.

---

### How It Works

Profesor Abelton runs **completely locally**:

1. GUI → local server (`127.0.0.1:8766`)
2. Server receives full session state via official **Control Surface Remote Script**
3. AI (Claude or Groq) returns structured tool calls
4. Commands are executed safely in Ableton Live

No cloud relay, no plugins, no MIDI mapping required.

---

### Supported Actions (40 total)

Full list of allowlisted actions includes:
- Track management (create, rename, move, group…)
- Mixer & routing (volume, pan, sends, mute, solo…)
- Clips & MIDI (create, edit notes, quantize, humanize, drum patterns…)
- Devices & effects (add, remove, set parameters, presets…)
- Transport & session (play, record, tempo, export audio…)

---

### Tech Stack

- **Backend:** Python + FastAPI/WebSocket
- **AI:** Claude (Model Context Protocol) + Groq (llama-3.3-70b)
- **Ableton Integration:** Official Control Surface Remote Script
- **Security:** Fernet encryption, strict allowlist, Bandit static analysis
- **Distribution:** Portable (Windows .exe bundle + macOS .app)

---

### Quick Start (Development)

```bash
git clone https://github.com/yourusername/profesor-abelton.git
cd profesor-abelton
pip install -r requirements.txt
python run.py
