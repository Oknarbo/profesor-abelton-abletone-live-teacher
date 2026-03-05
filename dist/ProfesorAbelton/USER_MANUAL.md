## USER MANUAL — Profesor Abelton (v2.0.0)

### Kanonska imena (VAŽNO)
- **Product name**: Profesor Abelton
- **Ableton Control Surface / Remote Script**: `ProfesorAbelton`

---

## 1) Preduvjeti
- Windows 10/11
- Ableton Live 10/11/12
- Internet (za GROQ/Claude)
- API key za **GROQ** i/ili **CLAUDE**

---

## 2) Instalacija

### Windows (najjednostavnije)
1. Otvori folder `PROFESOR_ABELTON_CLEAN`
2. Pokreni `install.bat`
3. Pričekaj da instalacija završi

### Mac/Linux
1. Otvori terminal u folderu `PROFESOR_ABELTON_CLEAN`
2. Pokreni:

```bash
chmod +x install.sh
./install.sh
```

---

## 3) Prvi start (Wizard)
Pri prvom pokretanju otvara se wizard koji:
- detektira Ableton “User Remote Scripts”
- instalira Remote Script kao folder `ProfesorAbelton`
- sprema API ključeve enkriptirano

Na kraju wizard-a obavezno **restartaj Ableton**.

---

## 4) Ableton setup (Control Surface)
U Abletonu:
1. Preferences → Link/Tempo/MIDI
2. Control Surface: **`ProfesorAbelton`**
3. Input/Output: None

---

## 5) Pokretanje
Najlakše: `start_all.bat` (Windows) / `start_all.sh` (Mac/Linux).

Alternativno:
- server: `start_server_only.bat`
- GUI: `start_gui_only.bat`

---

## 6) AI provideri (testirano)
U GUI-u su dostupni:
- **GROQ**
- **CLAUDE** (MCP / tool calling)

API ključeve unosiš u GUI pod Settings → API Keys.

---

## 7) Brzi test (3 komande)
U GUI napiši:
- “postavi novu midi traku”
- “postavi tempo na 128”
- “dodaj reverb na traku 1”

---

## 8) Troubleshooting (najčešće)

### Ne vidim `ProfesorAbelton` u Control Surface
- provjeri da postoji folder `ProfesorAbelton` u Ableton “User Remote Scripts”
- restartaj Ableton

### GUI: Disconnected
- server mora biti up
- port 8766 ne smije biti zauzet
- restart server + GUI

### Ableton: Waiting…
- Control Surface nije postavljen ili script nije učitan → provjeri i restartaj Ableton

