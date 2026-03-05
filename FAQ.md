## FAQ — Profesor Abelton

### 1) Koje ime trebam odabrati u Abletonu?
U Ableton Preferences → Link/Tempo/MIDI → Control Surface odaberi: **`ProfesorAbelton`**.

### 2) Ne vidim `ProfesorAbelton` u Control Surface dropdown-u. Zašto?
- Provjeri da folder postoji ovdje (Windows):  
  `%APPDATA%\Ableton\Live XX\Preferences\User Remote Scripts\ProfesorAbelton\__init__.py`
- Zatvori Ableton kompletno i ponovno ga pokreni.
- Ako si upravo instalirao skriptu, **restart Ableton je obavezan**.

### 3) GUI kaže “Disconnected” ili se ne spaja.
- Provjeri da je server pokrenut (npr. `start_server_only.bat` ili `start_all.bat`).
- Provjeri da port **8766** nije zauzet (firewall/antivirus).
- Restart server + GUI.

### 4) GUI kaže “Ableton: Waiting…”
- Najčešće Ableton nije učitao Remote Script.
- Provjeri Control Surface: **`ProfesorAbelton`**
- Restart Ableton.

### 5) Koji AI provideri su dostupni?
U ovoj verziji u UI su dostupni samo **GROQ** i **CLAUDE** (testirano). Ostali provideri dolaze kasnije nakon testiranja.

### 6) Treba li mi API key?
- **Da** za GROQ i/ili Claude (ovisno koji koristiš).
- Ključeve unosiš u GUI pod **Settings → API Keys** (spremaju se enkriptirano).

### 7) Radi li offline?
Trenutno je fokus na GROQ/Claude (cloud). Offline/local opcije dolaze u kasnijem updateu nakon testiranja.

### 8) Što trebam restartati nakon instalacije?
- Nakon instalacije Remote Script-a: **restart Ableton**
- Ako mijenjaš port ili provider: restart server

### 9) Je li MCP uključen?
Da — MCP je relevantan za Claude (tool calling). U GUI-u koristiš provider “CLAUDE”.

### 10) Gdje su logovi?
- Server: u njegovom konzolnom prozoru
- Ableton: Help → Show Log File
