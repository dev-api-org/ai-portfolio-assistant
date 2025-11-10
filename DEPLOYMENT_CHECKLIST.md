# Streamlit Cloud Deployment Checklist

Use this checklist before deploying to ensure everything is ready.

## ✅ Pre-Deployment Checklist

### Repository Structure
- [x] `requirements.txt` exists in root directory
- [x] `backend/__init__.py` exists (makes backend a Python package)
- [x] `__init__.py` exists in root directory
- [x] `.streamlit/config.toml` exists
- [x] `.streamlit/secrets.toml.example` exists (template only)
- [x] `.env.example` exists (template only)
- [x] `frontend/requirements.txt` removed (to avoid confusion)

### Security
- [x] `.env` is in `.gitignore`
- [x] `.streamlit/secrets.toml` is in `.gitignore`
- [ ] No API keys or secrets in code
- [ ] No `.env` file with real secrets committed
- [ ] No `.streamlit/secrets.toml` with real secrets committed

### Code Quality
- [x] All imports use proper package structure
- [x] `from backend import chat_core` ✅
- [x] `from frontend.components import file_upload` ✅
- [x] Streamlit secrets loaded into environment variables
- [x] Config supports both local (.env) and cloud (secrets) deployment

### Dependencies
- [x] All required packages in `requirements.txt`
- [x] Version constraints specified (e.g., `>=1.0.0,<2.0.0`)
- [x] No conflicting package versions

### Configuration Files
- [x] `.env.example` has all required variables documented
- [x] `.streamlit/secrets.toml.example` has correct TOML format
- [x] `README.md` has deployment instructions
- [x] `DEPLOYMENT.md` has detailed step-by-step guide

## 📋 Deployment Steps

### 1. Get Google AI API Key
- [ ] Visit https://aistudio.google.com/app/apikey
- [ ] Create or copy your API key
- [ ] Save it securely (you'll need it for step 4)

### 2. Commit and Push All Changes
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 3. Sign in to Streamlit Cloud
- [ ] Go to https://share.streamlit.io/
- [ ] Sign in with GitHub
- [ ] Authorize Streamlit

### 4. Create New App
- [ ] Click "New app"
- [ ] Repository: `dev-api-org/ai-portfolio-assistant`
- [ ] Branch: `main`
- [ ] Main file: `frontend/streamlit_chat_canvas.py`
- [ ] Python version: `3.10` or higher

### 5. Configure Secrets
Add in Streamlit Cloud secrets:
```toml
GOOGLE_API_KEY = "your_actual_api_key_here"
MODEL_NAME = "gemini-2.0-flash-exp"
MODEL_TEMPERATURE = "0.7"
```

### 6. Deploy
- [ ] Click "Deploy!"
- [ ] Wait for build to complete (2-5 minutes)
- [ ] Check build logs for errors

### 7. Test Deployment
- [ ] App loads successfully
- [ ] Chat interface works
- [ ] AI responds to messages
- [ ] No console errors
- [ ] All features functional

## 🔍 Post-Deployment Verification

### Functional Tests
- [ ] Send a test message
- [ ] Verify AI response
- [ ] Test different content types
- [ ] Check conversation history
- [ ] Test file upload (if applicable)

### Performance
- [ ] App loads in < 5 seconds
- [ ] Responses arrive in < 10 seconds
- [ ] No timeout errors
- [ ] No memory issues

### Security
- [ ] No API keys visible in UI
- [ ] No secrets in browser console
- [ ] No secrets in page source
- [ ] Secrets properly configured in Streamlit Cloud

## 🐛 Common Issues & Solutions

### Build Fails
- [ ] Check `requirements.txt` is in root
- [ ] Verify all `__init__.py` files exist
- [ ] Review build logs in Streamlit Cloud

### Runtime Errors
- [ ] Verify secrets are configured
- [ ] Check API key is valid
- [ ] Review app logs for details

### Import Errors
- [ ] Ensure `backend/__init__.py` exists
- [ ] Verify imports use correct paths
- [ ] Check Python version compatibility

## 📝 Maintenance Checklist

### Regular Tasks
- [ ] Monitor API usage and costs
- [ ] Check app performance metrics
- [ ] Review error logs weekly
- [ ] Update dependencies monthly
- [ ] Rotate API keys quarterly

### After Each Update
- [ ] Test locally first
- [ ] Commit and push changes
- [ ] Monitor deployment logs
- [ ] Verify functionality
- [ ] Check for errors

## 📞 Support Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Streamlit Forum**: https://discuss.streamlit.io/
- **Google AI Docs**: https://ai.google.dev/docs
- **Repository**: https://github.com/dev-api-org/ai-portfolio-assistant

## ✨ Success Criteria

Your deployment is successful when:
- ✅ App is accessible via public URL
- ✅ All features work as expected
- ✅ No errors in logs
- ✅ Secrets are secure
- ✅ Performance is acceptable
- ✅ Users can interact with AI

---

**Ready to deploy?** Follow the steps in [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
