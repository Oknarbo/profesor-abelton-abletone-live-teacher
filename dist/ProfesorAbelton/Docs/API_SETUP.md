# 🔑 API Setup Guide - Profesor Abelton

Complete guide for setting up AI provider API keys for Profesor Abelton.

---

## 🆓 Option 1: Ollama (FREE - Recommended for Beginners)

**No API keys needed! 100% local and free.**

### Windows

```batch
# 1. Download Ollama
# Go to: https://ollama.ai/download
# Download and run the installer

# 2. Open Command Prompt and start server
ollama serve

# 3. Open a new Command Prompt and download model
ollama pull llama3.1

# 4. Verify installation
ollama list
# You should see: llama3.1

# 5. Test it
ollama run llama3.1
# Type: Hello!
# You should get a response
```

### Mac

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start server
ollama serve &

# 3. Download model
ollama pull llama3.1

# 4. Test
ollama run llama3.1
```

### Linux

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start as service (automatically runs in background)
systemctl start ollama

# 3. Download model
ollama pull llama3.1

# 4. Verify
ollama list
```

**That's it! Profesor Abelton will automatically use Ollama.**

---

## 💰 Option 2: Cloud AI Providers

For more advanced models with better performance.

### OpenAI (GPT-4)

**Cost:** ~$0.01 per 1,000 tokens (very affordable)

#### 1. Create Account
- Go to: https://platform.openai.com/signup
- Sign up with email/Google
- Verify email

#### 2. Add Payment Method
- Go to: https://platform.openai.com/account/billing
- Add credit card
- Add $5-10 credit (lasts a long time)

#### 3. Create API Key
- Go to: https://platform.openai.com/api-keys
- Click "Create new secret key"
- Name it: "Profesor Abelton"
- Copy the key (starts with `sk-...`)
- ⚠️ **Save it safely - you can't see it again!**

#### 4. Set Environment Variable

**Windows:**
```batch
# Method 1: System Environment Variables
1. Press Win+R
2. Type: sysdm.cpl
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Variable name: OPENAI_API_KEY
6. Variable value: sk-your-key-here
7. Click OK on all dialogs
8. Restart your terminal/computer

# Method 2: Command Line (temporary)
set OPENAI_API_KEY=sk-your-key-here
```

**Mac/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc:
export OPENAI_API_KEY="sk-your-key-here"

# Apply changes:
source ~/.bashrc  # or ~/.zshrc

# Verify:
echo $OPENAI_API_KEY
```

#### 5. Configure Profesor Abelton

Edit `Config/copilot_config.json`:
```json
{
  "ai_providers": {
    "default": "GPT"
  }
}
```

---

### Anthropic (Claude)

**Cost:** ~$0.015 per 1,000 tokens

#### 1. Create Account
- Go to: https://console.anthropic.com/
- Sign up
- Verify email

#### 2. Get API Key
- Go to: https://console.anthropic.com/settings/keys
- Click "Create Key"
- Copy the key

#### 3. Set Environment Variable

**Windows:**
```batch
setx CLAUDE_API_KEY "your-key-here"
```

**Mac/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc:
export CLAUDE_API_KEY="your-key-here"
source ~/.bashrc
```

#### 4. Configure

```json
{
  "ai_providers": {
    "default": "CLAUDE"
  }
}
```

---

### xAI (Grok)

**Cost:** Varies

#### 1. Create Account
- Go to: https://console.x.ai/
- Sign up

#### 2. Get API Key
- Go to API Keys section
- Create new key
- Copy it

#### 3. Set Environment Variable

**Windows:**
```batch
setx GROK_API_KEY "your-key-here"
```

**Mac/Linux:**
```bash
export GROK_API_KEY="your-key-here"
```

#### 4. Configure

```json
{
  "ai_providers": {
    "default": "GROK"
  }
}
```

---

### Groq (FREE - Fast!)

**Cost:** FREE with rate limits

#### 1. Create Account
- Go to: https://console.groq.com/
- Sign up (no credit card needed!)

#### 2. Get API Key
- Go to: https://console.groq.com/keys
- Create new key
- Copy it

#### 3. Set Environment Variable

**Windows:**
```batch
setx GROQ_API_KEY "your-key-here"
```

**Mac/Linux:**
```bash
export GROQ_API_KEY="your-key-here"
```

#### 4. Configure

```json
{
  "ai_providers": {
    "default": "GROQ"
  }
}
```

---

## 🔄 Switching Between Providers

### Method 1: Config File

Edit `Config/copilot_config.json`:
```json
{
  "ai_providers": {
    "default": "OLLAMA"  // Change to: GPT, CLAUDE, GROK, or GROQ
  }
}
```

Restart the server.

### Method 2: GUI

In the Profesor Abelton GUI:
1. Find "AI:" dropdown
2. Select your provider
3. Commands will use that provider

---

## 🧪 Testing Your Setup

### Test OpenAI

```bash
# Windows Command Prompt
curl https://api.openai.com/v1/models ^
  -H "Authorization: Bearer %OPENAI_API_KEY%"

# Mac/Linux Terminal
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

Should return a list of models.

### Test Ollama

```bash
curl http://localhost:11434/api/tags
```

Should return installed models.

---

## 💡 Tips

### Cost Management

**OpenAI/Claude:**
- Set monthly spending limits in account settings
- Start with $5-10
- Monitor usage regularly
- Use GPT-4o-mini instead of GPT-4 (10x cheaper!)

**Free Options:**
- **Groq** - Free, fast, but with rate limits
- **Ollama** - Completely free, runs locally

### Best Practices

1. **Start with Ollama** - Learn the system for free
2. **Upgrade to Groq** - Still free, but faster/better
3. **Use GPT/Claude** - For complex tasks only

### Security

- ⚠️ **Never share API keys**
- ⚠️ **Don't commit to git**
- ⚠️ **Use environment variables**
- ✅ **Rotate keys regularly**
- ✅ **Set spending limits**

---

## ❓ Troubleshooting

### "API key not found"

```bash
# Check if environment variable is set:

# Windows:
echo %OPENAI_API_KEY%

# Mac/Linux:
echo $OPENAI_API_KEY

# Should show your key, not the variable name
```

**Fix:** Set the environment variable (see above)

### "Invalid API key"

- Check for typos
- Regenerate the key
- Make sure there are no extra spaces

### "Rate limit exceeded"

**Ollama:** Impossible (local)
**Groq:** Wait a few minutes
**OpenAI/Claude:** Add more credit or wait

### "Cannot connect to Ollama"

```bash
# Make sure Ollama is running:
ollama serve

# Check it's working:
ollama list
```

---

## 📊 Cost Comparison

| Provider | Cost | Speed | Quality | Free Tier |
|----------|------|-------|---------|-----------|
| Ollama | FREE | Medium | Good | ✅ Unlimited |
| Groq | FREE | Very Fast | Good | ✅ With limits |
| GPT-4o-mini | $0.15/1M | Fast | Very Good | $5 credit |
| GPT-4 | $5/1M | Fast | Excellent | $5 credit |
| Claude | $3/1M | Fast | Excellent | No |
| Grok | Varies | Fast | Good | No |

**Typical Usage:**
- Casual use: <$1/month with GPT-4o-mini
- Heavy use: $5-10/month

**Recommendation:**
1. **Beginners**: Ollama (free forever)
2. **Regular users**: Groq (free, fast)
3. **Professionals**: GPT-4o-mini (best value)
4. **Advanced**: GPT-4 or Claude (highest quality)

---

## 🎓 Next Steps

After setting up your API:

1. **Restart Profesor Abelton Server**
2. **Test with a simple command**
3. **Try different providers**
4. **Find what works best for you**

---

**Questions?** See README.md or contact support.

