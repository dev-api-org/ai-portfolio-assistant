# Streamlit Cloud Deployment Guide

This guide provides step-by-step instructions for deploying DevFolio AI to Streamlit Cloud.

## Pre-Deployment Checklist

Before deploying, ensure your repository has:

- [x] `requirements.txt` in the root directory
- [x] `backend/__init__.py` (empty file to make backend a package)
- [x] `__init__.py` in the root (empty file)
- [x] `.streamlit/config.toml` for Streamlit configuration
- [x] `.streamlit/secrets.toml.example` as a template
- [x] `.env.example` for local development reference
- [x] `.gitignore` includes `.env` and `.streamlit/secrets.toml`
- [x] All code committed and pushed to GitHub

## Step-by-Step Deployment

### 1. Prepare Your Google AI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the API key (you'll need it in step 4)

### 2. Sign in to Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Authorize Streamlit to access your repositories

### 3. Create New App

1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository:** `dev-api-org/ai-portfolio-assistant`
   - **Branch:** `main`
   - **Main file path:** `frontend/streamlit_chat_canvas.py`
3. Click **"Advanced settings"** (optional but recommended)
   - **Python version:** `3.10` or `3.11`
   - Leave other settings as default

### 4. Configure Secrets

**IMPORTANT:** Do this BEFORE clicking Deploy!

1. In the deployment form, find the **"Secrets"** section
2. Click to expand it
3. Add the following in TOML format:

```toml
# Required: Your Google AI API Key
GOOGLE_API_KEY = "your_actual_google_api_key_here"

# Optional: Model configuration
MODEL_NAME = "gemini-2.0-flash-exp"
MODEL_TEMPERATURE = "0.7"
```

4. Replace `your_actual_google_api_key_here` with your actual API key from step 1

### 5. Deploy

1. Review all settings
2. Click **"Deploy!"**
3. Wait for the build to complete (usually 2-5 minutes)

### 6. Monitor Deployment

Watch the build logs for:
- ✅ Dependencies installation
- ✅ App starting successfully
- ❌ Any errors (see Troubleshooting below)

### 7. Test Your App

Once deployed:
1. The app will automatically open
2. Test the chat functionality
3. Verify the AI responds correctly
4. Check that all features work

## Post-Deployment Configuration

### Update Secrets (if needed)

1. Go to your app in Streamlit Cloud
2. Click **"⋮"** (three dots) → **"Settings"**
3. Navigate to **"Secrets"**
4. Edit and save

### Update App

To deploy changes:
1. Commit and push to your GitHub repository
2. Streamlit Cloud will automatically rebuild
3. Or click **"Reboot app"** in settings to force rebuild

## Troubleshooting

### Build Fails: "ModuleNotFoundError: No module named 'backend'"

**Cause:** Missing `backend/__init__.py`

**Solution:**
```bash
# Create the file locally
touch backend/__init__.py
git add backend/__init__.py
git commit -m "Add backend __init__.py"
git push
```

### Build Fails: "ModuleNotFoundError: No module named 'langchain_google_genai'"

**Cause:** Missing or incorrect dependencies

**Solution:**
1. Verify `requirements.txt` exists in repository root
2. Check it contains: `langchain-google-genai>=1.0.0,<2.0.0`
3. Commit and push if modified

### Runtime Error: "API Key not found"

**Cause:** Secrets not configured

**Solution:**
1. Go to App Settings → Secrets
2. Add `GOOGLE_API_KEY = "your_key_here"`
3. Save and reboot app

### App Shows "Error: Invalid API Key"

**Cause:** Incorrect API key

**Solution:**
1. Verify key at [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Regenerate if necessary
3. Update in Streamlit Cloud secrets
4. Reboot app

### Import Errors

**Cause:** Incorrect import paths

**Solution:**
All imports should use:
- `from backend import chat_core` ✅
- `from frontend.components import file_upload` ✅
- NOT `import backend.chat_core` ❌

### App is Slow or Unresponsive

**Cause:** Rate limiting or API issues

**Solution:**
1. Check Google AI API quotas
2. Verify internet connectivity
3. Check Streamlit Cloud status page
4. Review app logs for errors

## Managing Your Deployment

### View Logs

1. Go to your app in Streamlit Cloud
2. Click **"Manage app"** (bottom right)
3. View real-time logs and metrics

### Reboot App

1. Go to App Settings
2. Click **"Reboot app"**
3. Wait for restart

### Delete App

1. Go to App Settings
2. Scroll to bottom
3. Click **"Delete app"**
4. Confirm deletion

## Security Best Practices

### ✅ DO:
- Use Streamlit Cloud secrets for API keys
- Keep `.env` in `.gitignore`
- Use `.env.example` for documentation
- Rotate API keys periodically
- Monitor usage and costs

### ❌ DON'T:
- Commit `.env` with real keys
- Share API keys publicly
- Hardcode secrets in code
- Use production keys for testing
- Ignore security warnings

## Cost Considerations

### Streamlit Cloud
- Free tier: 1 app, community support
- Paid tiers: More apps, custom domains, priority support

### Google AI API
- Free tier: Limited requests per minute
- Check current pricing at [Google AI Pricing](https://ai.google.dev/pricing)
- Monitor usage in Google Cloud Console

## Support

### Streamlit Cloud Issues
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Google AI API Issues
- [Google AI Documentation](https://ai.google.dev/docs)
- [Google AI Studio](https://aistudio.google.com/)

### App-Specific Issues
- Check repository issues on GitHub
- Review app logs in Streamlit Cloud
- Test locally first with `streamlit run frontend/streamlit_chat_canvas.py`

## Next Steps

After successful deployment:
1. ✅ Test all features thoroughly
2. ✅ Share your app URL
3. ✅ Monitor usage and performance
4. ✅ Gather user feedback
5. ✅ Iterate and improve

---

**Need help?** Check the main [README.md](README.md) for more information.
