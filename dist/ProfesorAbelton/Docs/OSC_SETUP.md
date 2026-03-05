# 🎛️ OSC Setup Guide
## Alternative to Max for Live

### Why OSC?
- **Industry Standard**: OSC (Open Sound Control) is the standard for music software communication
- **No Custom Scripts**: Works with Ableton's built-in OSC support
- **Universal**: Can communicate with any OSC-enabled device/software
- **Future-Proof**: OSC is widely supported in music production

### 🎯 What OSC Can Do
OSC can handle most Profesor Abelton commands, but has limitations compared to Max for Live:

#### ✅ What Works:
- Transport controls (play, stop, record)
- Track operations (create, volume, pan, mute, solo, arm)
- Tempo changes
- Clip creation
- Basic MIDI note addition

#### ⚠️ Limitations:
- Device creation requires manual intervention
- Browser navigation not available via OSC
- Some advanced features may be limited

---

## 🚀 Setup Steps

### 1. Enable OSC in Ableton Live 12

#### 🎯 **ABLETON LIVE 12 SPECIFIC INSTRUCTIONS**

**U Ableton Live 12, OSC postavke su možda na drugom mjestu:**

**Opcija A: Link MIDI Tab**
1. Otvori Ableton Live 12
2. Idi na **Preferences** → **Link MIDI** tab
3. Gledaj na dnu stranice za **OSC** sekciju
4. Ako vidiš OSC, enable-uj ga

**Opcija B: MIDI Tab**
1. **Preferences** → **MIDI** tab
2. Gledaj za OSC postavke

**Opcija C: Advanced Settings**
1. **Preferences** → **Advanced** tab
2. Gledaj za "OSC" ili "Network"

**Opcija D: Search Function**
1. U Preferences prozoru, koristi search bar (magnifying glass)
2. Ukucaj "OSC" i vidi što se pojavi

**Opcija E: Live Device Browser**
1. U Live Device Browser-u (desno), gledaj za OSC device
2. Možda ima "OSC" u MIDI Effects sekciji

#### 🔍 **Ako ne nađeš OSC u Preferences:**

**Mogući razlozi:**
- OSC je možda pod drugim imenom u Live 12
- Možda se zove "Open Sound Control"
- Možda je u "Remote" ili "Network" sekciji

**Alternative:**
1. Provjeri Ableton Live Manual za verziju 12
2. Search online: "Ableton Live 12 OSC setup"
3. Koristi "Live API" umjesto OSC-a

### 2. Verify OSC Connection
1. Start Profesor Abelton Server
2. Look for: `🎛️ OSC Communication: Enabled`
3. In GUI, look for: **Ableton 🟢 OSC**

### 3. If OSC is Not Available in Ableton 12

#### 🔄 **Fallback: Use Socket Communication (Remote Script)**

**Prednost:** Radi sa svim Ableton verzijama, više funkcionalnosti

**Setup:**
1. **Update Remote Script:**
   ```batch
   # Windows:
   update_remotescript.bat

   # Mac/Linux:
   cp RemoteScript/__init__.py ~/Music/Ableton/User\ Library/Remote\ Scripts/ProfesorAbelton/
   ```

2. **Restart Ableton Live 12**

3. **Verify Connection:**
   - Start server: `start_server_only.bat`
   - Start GUI: `start_gui.bat`
   - Look for: **Ableton 🟢 (Socket)**

#### 🎛️ **Alternative: Live API Browser**

Umjesto OSC-a, možeš koristiti:
1. **Live API Browser** u Ableton-u
2. To je debugging tool za programere
3. Idi na: **Help** → **Live API Browser**
4. Tu možeš vidjeti dostupne API funkcije

---

## 🔍 Troubleshooting Guide for Ableton 12

### "Cannot Find OSC Settings"

**Step 1: Check All Tabs**
```
Preferences Window Tabs:
├── Audio
├── MIDI
├── Link MIDI          ← Check here first
├── File Folder
├── Library
├── Advanced           ← Check here too
├── Record/Warp
└── CPU
```

**Step 2: Use Search**
- U Preferences prozoru, klikni na 🔍 (magnifying glass)
- Ukucaj: "OSC", "Open Sound Control", "Network", "Remote"

**Step 3: Check Live Version**
- Help → About Live
- Make sure you have Live 12.x.x

### "OSC Settings Found But Not Working"

**Common Issues:**
1. **Firewall:** Disable firewall temporarily
2. **Ports in Use:** Change ports to 9002/9003
3. **Localhost:** Try 127.0.0.1 instead of localhost

**Test OSC:**
1. Download free OSC app (TouchOSC, OSCulator)
2. Test basic OSC messages to port 9000
3. See if Ableton responds

---

## 💡 Alternative Solutions

### 1. **Use Max for Live (Paid)**
- Most reliable option
- Full device creation
- $99 one-time purchase

### 2. **Use Socket Communication**
- Works with remote script
- More features than OSC
- Current default method

### 3. **Wait for Updates**
- Ableton may add OSC back in future updates
- Check release notes for Live 12.x updates

---

## 📞 Need Help?

1. **Check Logs:**
   - Start server and look for OSC messages
   - Check Ableton log: Help → Show Log

2. **Test Commands:**
   ```
   "Create MIDI track"     ← Should work
   "Set tempo to 120"      ← Should work
   "Play"                  ← Should work
   ```

3. **Report Issues:**
   - Note exact Ableton version
   - Describe what you see in Preferences
   - Include server log messages

### 3. Test Basic Commands
Try these commands:
```
"Create new MIDI track"
"Set tempo to 128"
"Play"
"Stop"
```

---

## 🔧 Configuration

### Default OSC Settings
```json
{
  "osc": {
    "enabled": true,
    "ableton_receive_port": 9000,
    "server_send_port": 9001,
    "host": "127.0.0.1"
  }
}
```

### Custom Port Configuration
If ports 9000/9001 are in use, change them in `copilot_config.json`:
```json
{
  "ableton": {
    "osc": {
      "ableton_receive_port": 9002,
      "server_send_port": 9003
    }
  }
}
```

---

## 🎹 OSC vs Socket vs Max for Live

| Feature | Socket (Default) | OSC | Max for Live |
|---------|------------------|-----|--------------|
| **Setup Complexity** | Medium | Easy | Hard |
| **Device Creation** | Limited | Manual | Full |
| **Real-time** | ✅ | ✅ | ✅ |
| **Browser Access** | ❌ | ❌ | ✅ |
| **Cost** | Free | Free | $99+ |
| **Reliability** | High | High | Highest |

### Recommendation:
1. **Start with Socket** (current default) - easiest setup
2. **Try OSC** if you want industry standard communication
3. **Use Max for Live** for full device creation capabilities

---

## 🐛 Troubleshooting

### OSC Not Working
```
Symptoms: "OSC Communication: Disabled" in server logs
Solutions:
1. Install OSC library: pip install python-osc
2. Check ports are not in use by other applications
3. Verify Ableton OSC settings
4. Restart both Ableton and Profesor Abelton
```

### Commands Not Executing
```
Symptoms: Commands sent but no response
Solutions:
1. Check Ableton OSC is enabled
2. Verify port numbers match
3. Look for firewall blocking ports
4. Try different ports if 9000/9001 conflict
```

### Device Creation Still Manual
```
This is expected with OSC. For automatic device creation:
- Use Max for Live device
- Or use socket communication with remote script
```

---

## 📚 Advanced OSC Usage

### Custom OSC Messages
You can send custom OSC messages from other software:

```
/live/command/create_audio_track []
/live/command/set_tempo [128]
/live/command/play []
```

### Monitoring OSC Traffic
Use OSC monitoring tools like:
- **TouchOSC** (iOS/Android)
- **OSCulator** (Mac)
- **Processing** with oscP5 library

---

## 🎯 Next Steps

1. **Test OSC setup** with basic commands
2. **Compare with socket communication**
3. **Consider Max for Live** for full automation
4. **Contribute** to improve OSC implementation

**Questions?** Check the main README or create an issue!
