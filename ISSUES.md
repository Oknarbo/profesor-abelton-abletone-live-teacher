## ISSUES / BUG LIST (FAZA 5)

### Severity skala
- **CRITICAL**: blokira osnovni “happy path” (ne može se koristiti proizvod) ili rizik od gubitka podataka / security incident.
- **HIGH**: vrlo vjerojatno uzrokuje setup neuspjeh ili značajnu konfuziju za većinu korisnika.
- **MEDIUM**: djelomični kvar / edge-case koji se često događa, ali postoji workaround.
- **LOW**: minor UX/tekst/duplikat, ne blokira korištenje.
- **INFO**: napomena / tehnički dug.

---

### HIGH-001 — Nekonzistentno Control Surface / Remote Script ime (AICopilot vs ProfesorAbleton vs AI_Copilot) — FIXED

- **Severity**: HIGH *(historijski; riješeno)*
- **Impact**: korisnik može:
  - ne pronaći očekivani Control Surface u Abletonu, ili
  - instalirati skriptu pod jednim imenom, a u uputama dobije drugo,
  - završiti s “Connected” problemima i false-negative troubleshootingom.
- **Status nakon fixa**:
  - Kanonski naziv proizvoda: **Profesor Abelton**
  - Kanonski Control Surface / Remote Script name: **`ProfesorAbelton`**
  - `Config/copilot_config.json`: `ableton.remote_script_name` = `ProfesorAbelton`
  - Wizard/launcher/docs/installeri usklađeni na `ProfesorAbelton`
  - Installer best-effort briše legacy alias foldere (`AICopilot`, `AI_Copilot`, `ProfesorAbleton`) da izbjegne duplikate u Abletonu
- **Repro (najlakši)**:
  1. Pokreni novi setup (wizard) → “Install / Update” (instalira pod `ProfesorAbleton`, jer config tako kaže).
  2. Slijedi `Docs/QUICK_START.md` / `Docs/TUTORIAL_HR.md` i traži `AICopilot` u Ableton Preferences.
  3. Ovisno o stanju sistema, `AICopilot` se neće pojaviti (ili će se pojaviti drugi naziv), što zbunjuje i prekida onboarding.
- **Expected**:
  - Svi entry-pointovi (wizard, launcher tips, docs, installer) daju **isto ime**.
  - Ako se podržava legacy naziv, jasno je napisano: “odaberi ono što vidiš: `ProfesorAbleton` (novo) ili `AICopilot` (legacy)”.
- **Actual**:
  - Trenutno postoje najmanje tri različita stringa za isto (ili vrlo slično) značenje.
- **Suggested fix** (bez mijenjanja arhitekture):
  - Odabrati **kanonski** naziv (preporuka: `ProfesorAbleton`, jer je u configu i distu).
  - U dokumentaciji i launcher tekstovima uskladiti na kanonski naziv.
  - Legacy installer ili:
    - ažurirati da koristi config/wizard naming, ili
    - jasno označiti kao legacy/deprecated.
  - Opcionalno: instalirati oba foldera (`ProfesorAbleton` i `AICopilot`) kao alias (samo copy), ako želite smooth upgrade.

---

### MED-001 — Legacy Windows installer (`Installers/install_windows.py`) instalira Remote Script pod `AICopilot` — FIXED

- **Severity**: MEDIUM *(historijski; riješeno)*
- **Impact**: ako korisnik pokrene ovaj installer umjesto novog flowa, dobit će drugačiji naming i potencijalno mismatch s wizard/config.
- **Status nakon fixa**:
  - `Installers/install_windows.py` sada instalira u `.../User Remote Scripts/ProfesorAbelton`
- **Expected**: jedan installer path, jedan naziv, jedno uputstvo.
- **Actual**: legacy path ostavlja sustav u “split-brain” stanju.
- **Suggested fix**: deprecate ili uskladiti s `Utils/ableton_detector.py` + `Config/copilot_config.json`.

---

### LOW-001 — Launcher quick tips spominje `AI_Copilot` (underscore) koji nije default nigdje drugdje — FIXED

- **Severity**: LOW *(historijski; riješeno)*
- **Impact**: dodatna konfuzija (tekstualni hint).
- **Lokacija**: `launch_profesor_ableton.py` (`show_quick_tips()`).
- **Suggested fix**: zamijeniti string s kanonskim nazivom iz configa ili ispisati “Control Surface: <script_name>” kao u auto-install poruci.

---

### LOW-002 — Duplikat instrumenta “Simpler” u `copilot_config.json`

- **Severity**: LOW
- **Impact**: minimalno (kozmetika / data quality).
- **Lokacija**: `Config/copilot_config.json` → `ableton.available_instruments` sadrži “Simpler” dvaput.
- **Suggested fix**: ukloniti duplikat.

---

### INFO-001 — “ProfesorAbelton” vs “ProfesorAbleton” (spelling drift u dokumentima) — FIXED

- **Severity**: INFO *(historijski; riješeno)*
- **Impact**: konfuzija u komunikaciji, posebno u handoff dokumentima i uputama.
- **Status nakon fixa**: standardizirano na `ProfesorAbelton` (Control Surface/Remote Script) + “Profesor Abelton” (product name).

---

### OPEN — Preostali build artefakti koriste stare nazive (ne utječe na runtime, ali utječe na branding)

- **Severity**: LOW
- **Primjeri**: `dist/ProfesorAbleton/ProfesorAbleton.exe`, `ProfesorAbleton.spec`, razni `build/*` `.toc` fajlovi.
- **Preporuka**: napraviti rebuild packaginga s novim `--name` i očistiti `build/` + `dist/` prije builda.

