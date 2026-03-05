# Profesor Abelton - macOS Build

## 🚀 Automatski macOS Build

Ovaj repository koristi GitHub Actions za automatski build macOS aplikacije.

### Kako radi:

1. **Push kod** na GitHub
2. **GitHub automatski** pokreće macOS build
3. **Downloadajte** gotovu aplikaciju iz Actions tab-a

### Za developere:

#### Lokalni macOS build:
```bash
chmod +x build_mac.sh
./build_mac.sh
```

#### Rezultati:
- `dist/ProfesorAbelton.app` - macOS aplikacija
- `release/ProfesorAbelton_macOS_v2.0.0.zip` - ZIP za distribuciju

### GitHub Actions workflow:

- **Pokreće se na:** push na main/master branch
- **Koristi:** macOS-latest runner (pravi macOS)
- **Trajanje:** 5-10 minuta
- **Rezultat:** macOS .app fajl i ZIP

### Download build-a:

1. Idite u **Actions** tab
2. Kliknite na zadnji workflow
3. Dole downloadajte **macos-build** artifact

---
**Napomena:** GitHub Actions koristi Intel macOS, ali aplikacija radi na Apple Silicon-u.