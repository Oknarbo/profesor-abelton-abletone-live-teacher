# Profesor Abelton

**Version:** 2.0.0  
**Supported AI providers (in UI):** **Groq** + **Claude (MCP tools)**  
**Ableton Control Surface / Remote Script name:** `ProfesorAbelton`

Profesor Abelton is an AI assistant for Ableton Live that lets you control your session using natural language. Claude runs in **MCP tool mode** (35 tools) for reliable structured “action calls”, and Groq is available as a fast fallback.

> Not affiliated with Ableton. “Profesor Abelton” is a wordplay brand name.

---

## Features
- **Direct Ableton control**: create tracks/clips, set tempo, add devices, transport control, basic mixing controls
- **Claude MCP (35 tools)**: structured tool calling → predictable Ableton actions
- **Groq fallback**: fast parsing + execution
- **First Launch Wizard**: installs the Remote Script and guides setup
- **Encrypted API key storage** (per-machine)

---

## Requirements
- **OS**: Windows 10/11 (macOS/Linux supported best-effort)
- **Ableton Live**: 10 / 11 / 12 (tested on Live 12.x)
- **Python**: 3.9+ recommended
- Internet connection (for Groq/Claude)

---

## Quick Start (Windows)
1. **Install**
   - Run `install.bat`
2. **Start**
   - Run `start_all.bat` (recommended)
3. **Wizard**
   - Install/update Remote Script
   - Enter API keys (Groq and/or Claude)
4. **Ableton setup**
   - Ableton Preferences → Link/Tempo/MIDI → Control Surface: **`ProfesorAbelton`**
   - Input/Output: None
   - Restart Ableton
5. **Try commands**
   - “create a new midi track”
   - “set tempo to 128”
   - “add reverb to track 1”

---

## Quick Start (macOS/Linux)
1. Run:

```bash
chmod +x install.sh
./install.sh
```

2. Start:

```bash
./start_all.sh
```

3. In Ableton, set Control Surface to **`ProfesorAbelton`** and restart Ableton.

---

## Supported AI Providers (currently)
In the GUI you can select:
- **GROQ**
- **CLAUDE** (MCP tools enabled)

Other providers/local modes can be added later after testing.

---

## Troubleshooting (most common)

### I don’t see `ProfesorAbelton` in Ableton Control Surface
- Make sure the Remote Script was installed and that this file exists:
  - Windows: `%APPDATA%\Ableton\Live XX\Preferences\User Remote Scripts\ProfesorAbelton\__init__.py`
- Restart Ableton completely.

### GUI says “Disconnected”
- Make sure the server is running (`start_all.bat` or `start_server_only.bat`)
- Check port **8766** is free / allowed by firewall

### GUI says “Ableton: Waiting…”
- Set Control Surface to **`ProfesorAbelton`**
- Restart Ableton

---

## Documentation
- `Docs/QUICK_START.md`
- `Docs/TUTORIAL_EN.md`
- `Docs/API_SETUP.md`
- `Docs/OSC_SETUP.md` (optional)

---

## Support
- Discord: *(add link)*
- Email: *(add support email)*

