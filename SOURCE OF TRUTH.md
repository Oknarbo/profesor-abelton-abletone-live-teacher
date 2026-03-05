🎓 PROFESOR ABELTON - HANDOFF DOCUMENTATION
Last Updated: 2026-02-10
Status: ✅ Core Complete → 🚧 Pre-Production Phase
Next Milestone: Gumroad Launch (MVP)
A) HANDOFF SUMMARY
1️⃣ Cilj Projekta
Profesor Abelton = AI-powered asistent za Ableton Live koji omogućuje:
Kreiranje traka, clipova, instrumenata govornim/tekstualnim komandama
Claude MCP direktna integracija (Claude poziva Ableton funkcije kao native tools)
Multi-provider support (trenutno u UI: GROQ + Claude MCP; ostali provideri planirani nakon testiranja)
Natural language commands (HR/EN): "postavi novu midi traku", "dodaj reverb na traku 1"
Business cilj: Launch na Gumroad kao paid product ($19.99) ili open-source sa donations.
2️⃣ Što Već Radi ✅
CORE FUNCTIONALITY (100% radno):
✅ GUI (Tkinter) ↔ Server (Python Socket) komunikacija
✅ Server ↔ Ableton Live Remote Script komunikacija
✅ Claude MCP integration - Claude direktno poziva 35+ Ableton funkcija
✅ GROQ JSON command parsing (backup metoda)
✅ Remote Script instaliran u Ableton (ProfesorAbelton folder)
✅ Real-time state monitoring (tracks, tempo, devices)
✅ Persistent socket connection između servera i Abletona
TESTIRANO:
Windows 10/11 + Ableton Live 12.2.5
Claude Opus 4 model (claude-opus-4-20250514)
Kreiranje traka, postavljanje tempa, dodavanje nota, drum patterns
Multiple simultane komande (6+ commands u jednom requestu)
3️⃣ Ključne Odluke
Odluka	Razlog	Implikacija
Claude MCP preko Anthropic API	Native tool calling, elegantnija integracija od JSON parsinga	Potreban Claude API key ($5 credit minimum)
Socket komunikacija umjesto OSC	Pouzdanija, real-time state updates	Zahtijeva Python Remote Script u Abletonu
Newline delimiter (\n) za poruke	Riješava parsing multiple messages u bufferu	Svi send/recv moraju koristiti + b'\n'
ProfesorAbelton naziv foldera	Izbjegava conflict sa Python built-in "RemoteScript"	Korisnik mora odabrati "ProfesorAbelton" u Control Surface
Config u ~/.profesor_abelton/	User-specific, ne hard-coded paths	Lako za multi-user, backup-friendly
Claude Haiku/Opus 4 modeli	Samo ti rade na user's accountu (testirali via API)	Ne koristiti Claude 3.5 Sonnet modele
4️⃣ Ograničenja (NE DIRATI!) 🚨
ARHITEKTURA:
❌ NE mijenjaj socket protokol (newline delimiter + JSON format)
❌ NE remiksaj MCP tool definitions u serveru - Claude ih već razumije
❌ NE diraj Remote Script __init__.py bez testiranja u Abletonu - lako se pokvari
❌ NE hardcodiraj API keyeve u kod ili config fajlove (security!)
KOMPATIBILNOST:
Server MORA podržavati i MCP (Claude) i JSON parsing (GROQ) istovremeno
GUI mora raditi bez servera (prikaz "Not Connected" umjesto crasha)
Remote Script mora raditi i kad server nije pokrenut (ne crashati Ableton)
FILE STRUCTURE:
PROFESOR_ABELTON_CLEAN/
├── GUI/
│   ├── profesor_ableton_gui.py   # Main GUI
│   └── first_launch_wizard.py    # First launch wizard
├── Server/
│   └── ai_copilot_server.py      # Socket server + LLM integration (Claude MCP + Groq parsing)
├── RemoteScript/
│   └── __init__.py               # Ableton Remote Script (delicate!)
├── Utils/
│   ├── ableton_detector.py       # Auto-detect + auto-install Remote Script
│   └── api_key_manager.py        # Encrypted API key storage
├── Config/
│   ├── copilot_config.json       # Providers/models (NO API keys here!)
│   └── env_example.txt
├── Docs/
│   └── ...                       # Quick start / tutorials / API setup
├── SOURCE OF TRUTH.md
└── launch_profesor_abelton.py    # Main launcher
5️⃣ Otvorena Pitanja / Sljedeći Koraci
IMMEDIATE (Pre-Launch MVP):
🔐 API Key Encryption - trenutno u plain JSON (SECURITY RISK!)
🤖 Ableton Auto-Detection - korisnik mora ručno kopirati Remote Script
🧙 First Launch Wizard - setup experience za nove korisnike
📦 PyInstaller Packaging - .exe (Windows) + .app (Mac)
⚠️ User-Friendly Errors - trenutno tehnički error messagesi
NICE-TO-HAVE (Post-Launch):
Voice control (Speech Recognition već u kodu ali ne aktiviran)
Theme support (Light/Dark)
Chat history save/load
Multi-language (HR/EN switch)
Statistics dashboard
6️⃣ Relevantni Detalji
DEPENDENCIES:
# Corerequests==2.31.0python-osc==1.8.3  # (optional, not currently used)# GUItkinter (built-in)pillow (optional, za system tray)pystray (optional, minimize to tray)# Voice (optional)SpeechRecognitionpyaudio  # (problematičan na Macu)# Ableton Remote Script# → Python 2.7 compatible! (Ableton still uses Python 2)
ENVIRONMENT VARIABLES:
# Currently loaded from copilot_config.json, should move to:CLAUDE_API_KEY=sk-ant-...GROQ_API_KEY=gsk_...GPT_API_KEY=sk-...
KEY FILES:
ai_copilot_server.py:1318 → MCP command handling (nedavno fixano!)
ai_copilot_server.py:453 → Claude MCP tool definitions (35 tools)
__init__.py:1200 → Remote Script command execution loop
profesor_ableton_gui.py:565 → GUI send_to_server (connect + command flow)
TESTING COMMANDS:
# Start server
cd PROFESOR_ABELTON_CLEAN/Server
python ai_copilot_server.py

# Start GUI (separate terminal)
cd PROFESOR_ABELTON_CLEAN/GUI
python profesor_ableton_gui.py

# Test commands in GUI:
"postavi novu midi traku"
"postavi tempo na 128"
"dodaj reverb na traku 1"
GIT/BACKUP:
Remote Script backup: RemoteScript/__init__.py.bak (keep it!)
Config backup: Prije bilo koja promjena, backup copilot_config.json
B) SWARM PLAN - 6-AGENT ARCHITECTURE
🎯 Overall Strategy: Sequential Pipeline + Review Gates
Philosophy: Svaki agent radi jedan task perfektno, zatim hand-off sljedećem. QA Agent ima VETO na svakom checkpoint-u.
🤖 AGENT 1: SECURITY AGENT
Codename: sec-agent
Scope: API key management, encryption, secure storage
Tasks:
✅ Implementiraj Utils/api_key_manager.py sa Fernet encryption
✅ Machine-specific encryption key (hash of machine ID)
✅ Integriraj u GUI (replace self.api_keys dict)
✅ Testiraj: spremi key → restart app → key se učita
✅ Security audit: provijeri nema API keyeva u logu/config
Allowed Actions:
✅ Create new files: Utils/api_key_manager.py
✅ Edit: GUI/profesor_ableton_gui.py
❌ NE DIRAJ: Server, Remote Script, config.json API keys section
Definition of Done:
[ ] API keys stored in ~/.profesor_abelton/keys.encrypted
[ ] Fernet encryption sa SHA256(machine_id) key
[ ] GUI load/save preko APIKeyManager klase
[ ] Unit test: encrypt → decrypt → verify
[ ] Zero API keys in git repo ili config files
Output Format:
# sec-agent-report.md## Files Changed:- Created: Utils/api_key_manager.py (127 lines)- Modified: GUI/profesor_ableton_gui.py (settings integration)## Test Results:✅ Encryption/Decryption test passed✅ Machine-specific key generation works✅ GUI integration: save/load API key successful## Security Checklist:✅ No plaintext API keys in code✅ No API keys in logs⚠️ Warning: User must manually delete old config.json keys## Handoff to INSTALL-AGENT: Ready ✅
🤖 AGENT 2: INSTALLATION AGENT
Codename: install-agent
Scope: Ableton detection, Remote Script auto-install, system integration
Tasks:
✅ Implementiraj Utils/ableton_detector.py (Windows + Mac paths)
✅ Auto-detect Ableton install path + version
✅ Auto-copy RemoteScript/ → Ableton User Remote Scripts/ProfesorAbelton/
✅ Detect if Ableton is running (psutil)
✅ Handle permissions errors (Windows UAC, Mac SIP)
Allowed Actions:
✅ Create: Utils/ableton_detector.py
✅ Edit: launch_profesor_ableton.py (add auto-install step)
✅ Install dependency: psutil
❌ NE DIRAJ: Remote Script __init__.py sam (samo copy operacija)
Definition of Done:
[ ] Detect Ableton na Windows (ProgramFiles/Ableton/Live /)
[ ] Detect Ableton na Mac (/Applications/Ableton Live .app)
[ ] Get Remote Scripts path (AppData/Roaming ili ~/Library/Preferences)
[ ] Copy RemoteScript → ProfesorAbelton folder (sa error handling)
[ ] CLI test script: python test_detection.py prikazuje sve pathove
Output Format:
# install-agent-report.md## Files Changed:- Created: Utils/ableton_detector.py (156 lines)- Modified: launch_profesor_ableton.py (added auto_install_remote_script())- Added: requirements.txt → psutil==5.9.0## Platform Tests:✅ Windows 10: Detected Ableton Live 11 Suite (C:\Program Files\Ableton\...)✅ Windows 11: Detected Ableton Live 12 (C:\Program Files\Ableton\...)⚠️ Mac: Not tested (no Mac available)## Edge Cases Handled:✅ Multiple Ableton versions → uses latest✅ Ableton not installed → graceful error✅ Permission denied → instructions for manual install## Handoff to WIZARD-AGENT: Ready ✅
🤖 AGENT 3: WIZARD AGENT
Codename: wizard-agent
Scope: First launch experience, onboarding wizard, UX flow
Tasks:
✅ Implementiraj GUI/first_launch_wizard.py (5-page wizard)
✅ Page 1: Welcome screen
✅ Page 2: Ableton detection (use ableton_detector.py)
✅ Page 3: Remote Script installation (one-click install)
✅ Page 4: API keys setup (use api_key_manager.py)
✅ Page 5: Test connection + Finish
Allowed Actions:
✅ Create: GUI/first_launch_wizard.py
✅ Edit: launch_profesor_ableton.py (call wizard before main GUI)
✅ Use: APIKeyManager, AbletonDetector klase
❌ NE MIJENJAJ: Core funkcionalnost GUI/Server
Definition of Done:
[ ] Wizard shows only on first launch (check ~/.profesor_abelton/setup_complete)
[ ] All 5 pages functional with Next/Back navigation
[ ] Remote Script install works with progress feedback
[ ] API key form validation (ne dozvoli prazne keyeve)
[ ] Final page: clear instructions ("Restart Ableton → Select ProfesorAbelton")
Output Format:
# wizard-agent-report.md## Files Changed:- Created: GUI/first_launch_wizard.py (342 lines)- Modified: launch_profesor_ableton.py (added show_first_launch_wizard())## UX Flow:1. Welcome → 2. Detect Ableton → 3. Install Script → 4. API Keys → 5. Finish   ✅ All transitions smooth   ✅ Back button works on all pages except first## User Testing Feedback:✅ Clear instructions on each page✅ One-click install button works⚠️ Suggestion: Add "Skip wizard" option for advanced users## Handoff to PACKAGING-AGENT: Ready ✅
🤖 AGENT 4: PACKAGING AGENT
Codename: pkg-agent
Scope: PyInstaller setup, .exe/.app creation, dependency bundling
Tasks:
✅ Setup PyInstaller spec file (Windows)
✅ Bundle all dependencies (requests, tkinter, cryptography, psutil)
✅ Include: Config/, RemoteScript/ folders
✅ Test .exe na clean Windows VM (ako moguće)
✅ Document build process (README_BUILD.md)
Allowed Actions:
✅ Create: profesor_abelton.spec (PyInstaller config)
✅ Create: build_windows.bat, build_mac.sh
✅ Edit: requirements.txt (dodaj pyinstaller)
❌ NE MIJENJAJ: Python kod (samo packaging)
Definition of Done:
[ ] PyInstaller spec file compiles bez errora
[ ] .exe size razuman (< 100MB)
[ ] .exe startuje i pokreće GUI na clean system
[ ] Remote Script folder uključen u bundle
[ ] Config folder kreiran na first run ako ne postoji
Output Format:
# pkg-agent-report.md## Build Process:# Windowspyinstaller profesor_abelton.spec# Output: dist/ProfesorAbelton.exe (87.3 MB)
Test Results:
✅ Windows 10 VM: .exe starts, GUI loads
✅ All dependencies bundled correctly
⚠️ Warning: Large .exe size due to tkinter + requests
Build Files Created:
profesor_abelton.spec (PyInstaller config)
build_windows.bat (one-click build script)
README_BUILD.md (build instructions)
Known Issues:
[ ] Mac .app not tested (no Mac system available)
[ ] Code signing not implemented (future task)
Handoff to TEST-AGENT: Ready ✅
---## 🤖 AGENT 5: TESTING AGENT**Codename:** `test-agent`  **Scope:** Multi-platform testing, bug discovery, edge case handling### Tasks:- ✅ Test matrix: Windows 10/11, Mac (if available), Ableton 11/12- ✅ Test all core features: create track, set tempo, add device, etc.- ✅ Test error scenarios: no Ableton, wrong API key, no internet- ✅ Stress test: 50+ commands rapid-fire- ✅ Document bugs in `ISSUES.md`### Allowed Actions:- ✅ Run tests, document results- ✅ Create: `ISSUES.md`, `TEST_REPORT.md`- ✅ Minor bug fixes (če su očiti typo/logic errors)- ❌ NE MIJENJAJ: Arhitekturu bez QA Agent odobrenja### Definition of Done:- [ ] Core functionality tested na minimum 2 platforme- [ ] All 35 MCP tools testirane (bar 20+)- [ ] Edge cases documented- [ ] Bug severity classified (Critical/High/Medium/Low)- [ ] Regression test suite kreiran (automated ili manual checklist)### Output Format:# test-agent-report.md## Test Matrix:| OS | Ableton | Result | Notes ||----|---------|--------|-------|| Win 10 | Live 12.2.5 | ✅ PASS | All features work || Win 11 | Live 11.3 | ✅ PASS | Minor UI glitch || Mac 13 | Live 12.2.5 | ⚠️ PARTIAL | Voice not working |## Core Features (35/35 tested):✅ create_midi_track → Works✅ create_audio_track → Works✅ set_tempo → Works... (list all)## Bugs Found:🔴 CRITICAL: None🟠 HIGH:   - #1: GUI freeze on rapid commands (> 10/sec)🟡 MEDIUM:  - #2: Error message shows technical details🟢 LOW:  - #3: Typo in welcome message## Stress Test:✅ 50 commands in 30 seconds → No crashes✅ 100 tracks created → Ableton slow but stable## Handoff to DOC-AGENT: Ready ✅
🤖 AGENT 6: DOCUMENTATION AGENT
Codename: doc-agent
Scope: User manual, quick start, FAQ, video script
Tasks:
✅ Kreiraj USER_MANUAL.md (installation, setup, usage)
✅ Kreiraj QUICK_START.pdf (1-page guide sa screenshotima)
✅ Kreiraj FAQ.md (top 10 pitanja)
✅ Kreiraj VIDEO_SCRIPT.md (5-min tutorial outline)
✅ Update README.md (GitHub/Gumroad landing page)
Allowed Actions:
✅ Create: All documentation files
✅ Edit: README.md (make it professional)
✅ Take screenshots (GUI, Ableton setup, wizard)
❌ NE MIJENJAJ: Kod (samo dokumentacija)
Definition of Done:
[ ] USER_MANUAL.md covers: install, first launch, basic usage, troubleshooting
[ ] QUICK_START.pdf sa screenshot every step
[ ] FAQ.md odgovara na minimum 10 pitanja
[ ] README.md ima: features, screenshots, installation, pricing
[ ] VIDEO_SCRIPT.md ready za recording (time-stamped)
Output Format:
# doc-agent-report.md## Files Created:- USER_MANUAL.md (2,847 words, 12 sections)- QUICK_START.pdf (1 page, 6 screenshots)- FAQ.md (15 Q&As)- VIDEO_SCRIPT.md (5:23 duration, shot-by-shot)- README.md (updated, professional)## Documentation Coverage:✅ Installation (Windows + Mac step-by-step)✅ First Launch Wizard walkthrough✅ API Key setup instructions✅ Basic Commands (20 examples)✅ Troubleshooting (8 common issues)✅ Advanced Tips (5 power-user tricks)## Screenshots Taken:- GUI_overview.png- Ableton_control_surface_setup.png- First_launch_wizard_page1.png... (12 total)## Handoff to QA-AGENT: Final Review Ready ✅
🎛️ SWARM ORCHESTRATION
Workflow:
┌─────────────────┐│  START PROJECT  │└────────┬────────┘         │    ┌────▼──────────────────┐    │  QA-AGENT (Planning)  │──────┐    │  - Review handoff     │      │    │  - Approve scope      │      │ VETO if unclear    │  - Assign priorities  │      │    └────────┬──────────────┘      │             │                     │    ┌────────▼──────────────┐      │    │  1. SECURITY-AGENT    │◄─────┘    │  (API encryption)     │    └────────┬──────────────┘             │    ┌────────▼──────────────┐    │  QA Review Point 1    │──────┐    │  - Security audit     │      │ VETO if insecure    │  - Approve handoff    │      │    └────────┬──────────────┘      │             │                     │    ┌────────▼──────────────┐      │    │  2. INSTALL-AGENT     │◄─────┘    │  (Ableton detection)  │    └────────┬──────────────┘             │    ┌────────▼──────────────┐    │  QA Review Point 2    │    └────────┬──────────────┘             │    ┌────────▼──────────────┐    │  3. WIZARD-AGENT      │    │  (First launch UX)    │    └────────┬──────────────┘             │    ┌────────▼──────────────┐    │  QA Review Point 3    │    └────────┬──────────────┘             │    ┌────────▼──────────────┐    │  4. PACKAGING-AGENT   │    │  (PyInstaller build)  │    └────────┬──────────────┘             │    ┌────────▼──────────────┐    │  5. TESTING-AGENT     │    │  (Multi-platform QA)  │    └────────┬──────────────┘             │    ┌────────▼──────────────┐    │  6. DOC-AGENT         │    │  (User manual, FAQ)   │    └────────┬──────────────┘             │    ┌────────▼──────────────┐    │  QA-AGENT (Final)     │    │  - Integration test   │    │  - Gumroad readiness  │    │  - APPROVE LAUNCH     │    └───────────────────────┘
Review Gates:
Checkpoint	Reviewer	Veto Criteria	Action on Veto
After SEC	QA-AGENT	API key found in plaintext	Block INSTALL
After INSTALL	QA-AGENT	Auto-install doesn't work	Block WIZARD
After WIZARD	QA-AGENT	UX flow confusing	Block PACKAGING
After PKG	QA-AGENT	.exe doesn't run	Block TESTING
After TEST	QA-AGENT	Critical bug found	Return to relevant agent
After DOC	QA-AGENT	Missing critical docs	Block LAUNCH
Coordination Rules:
No Parallel Work - Agents run sequentially (dependencies!)
Max 1 Agent Active at a time (prevent conflicts)
Short Iterations - Each agent max 2h session, then checkpoint
Clear Handoffs - Agent must explicitly say "Handoff to X-AGENT: Ready ✅"
QA Has Final Say - QA-AGENT can veto ANY agent's work
📋 AGENT LIMITATIONS
Token Budget per Agent:
Security: 50k tokens (mostly code gen)
Install: 40k tokens (file operations + testing)
Wizard: 60k tokens (GUI + UX)
Packaging: 30k tokens (config files mostly)
Testing: 40k tokens (manual testing, reports)
Documentation: 50k tokens (writing heavy)
Time Limits:
Each agent: Max 2h real-time session
If not done → Save state → Handoff to QA for re-assignment
File Edit Rules:
# Each agent can ONLY edit files in their scope:SEC-AGENT:     Utils/*, GUI/*_gui.py (API key logic only)INSTALL-AGENT: Utils/ableton_detector.py, launch_*.pyWIZARD-AGENT:  GUI/first_launch_wizard.py, launch_*.pyPKG-AGENT:     *.spec, build_*.bat/sh, requirements.txtTEST-AGENT:    TEST_*.md, ISSUES.md (read-only on code)DOC-AGENT:     *.md, *.pdf (no code changes)QA-AGENT:      Can review ALL, edit NONE (only approve/reject)
🚦 SUCCESS CRITERIA
MVP Ready for Gumroad when:
[ ] QA-AGENT approves final integration test
[ ] Zero CRITICAL bugs
[ ] Windows .exe tested na clean VM
[ ] USER_MANUAL.md complete
[ ] QUICK_START.pdf ready
[ ] README.md professional
Launch Checklist:
✅ Security audit passed (no API keys leaked)✅ Auto-installer works (tested 3x)✅ First launch wizard flows smoothly✅ .exe runs on clean Windows 10/11✅ All core features tested (35/35)✅ Documentation complete✅ Gumroad listing drafted
💬 COMMUNICATION PROTOCOL
Agent Report Template:
# {AGENT-NAME}-report-{DATE}.md## Summary (3 sentences)- What was done- What works- What's blocked## Files Changed- Created: [list]- Modified: [list]- Deleted: [list]## Tests Passed- [Test 1]: ✅/❌- [Test 2]: ✅/❌## Blockers- [Issue 1]: Description + severity- [Issue 2]: ...## Handoff- Next Agent: {NAME}- Status: Ready ✅ / Blocked ❌- Notes for next agent: [critical info]## QA-AGENT Review Request@qa-agent Please review: [specific items]
🎯 START COMMAND
To initialize swarm:
@qa-agentProject: Profesor Abelton Pre-LaunchPhase: FAZA 1 - Security & InstallationCurrent status: See HANDOFF SUMMARY aboveFirst assignment: SEC-AGENT → API Key EncryptionPlease review handoff doc and approve/modify swarm plan.When ready, dispatch SEC-AGENT with specific task breakdown.
🎊 CLOSING NOTES
Projekt Status: Core je 100% funkcionalan i production-ready u smislu funkcionalnosti. Treba samo packaging i polish za end-users.
Estimated Timeline:
FAZA 1 (Agents 1-3): 2-3 dana
FAZA 2 (Agents 4-6): 2-3 dana
Total MVP: ~1 tjedan full-time ili 2 tjedna part-time
Risk Mitigation:
Backup prije svake agent sesije: git commit -m "Pre-{agent-name}"
Test na clean VM prije handoffa
QA-AGENT ima override na sve odluke