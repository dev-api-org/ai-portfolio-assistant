# AI Portfolio Assistant

An intelligent Streamlit app that helps you create professional portfolio content through natural conversation. Chat with the AI to generate comprehensive README-style profiles, project summaries, and learning reflections.

## Features

- **Personal Bio Generation**: Create professional profiles with contact info, skills, and experience
- **Project Summaries**: Generate detailed project descriptions and technical documentation  
- **Learning Reflections**: Document learning objectives, skills acquired, and future goals
- **Live Preview**: See your content update in real-time as you chat
- **Smart Information Extraction**: AI automatically extracts and organizes your professional details

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-portfolio-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root with your Google API key:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   MODEL_NAME=gemini-2.0-flash
   MODEL_TEMPERATURE=0.7
   ```
   
   Get your Google API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Usage

1. **Run the app**
   ```bash
   streamlit run app.py
   ```

2. **Start chatting**
   - Share your professional background naturally
   - Include details about your experience, skills, and projects
   - Watch as the AI generates polished README content in real-time

3. **Switch modes**
   - **Personal Bio**: Professional profile and resume content
   - **Project Summaries**: Technical project documentation
   - **Learning Reflections**: Educational and skill development content

## Requirements

- Python 3.8+
- Google API key for Gemini AI
- Internet connection for AI model access

## Project Structure

```
ai-portfolio-assistant/
├── app.py                    # Main application entry point
├── requirements.txt          # Python dependencies
├── backend/                  # Core logic and AI integration
├── frontend/                 # Streamlit UI components
├── tests/                    # Test suite
├── docs/                     # Deployment documentation
├── configs/                  # Cloud-specific configuration
└── .github/workflows/        # CI/CD pipeline
```

## Development & Testing

**Run tests:**
```bash
python -m pytest tests/ -v
```

**Test coverage:**
```bash
pytest --cov=backend --cov=frontend tests/
```

## Deployment

This project supports deployment to multiple cloud platforms:

- **AWS**: See [docs/aws_setup.md](docs/aws_setup.md)
- **Azure**: See [docs/azure_setup.md](docs/azure_setup.md)  
- **CI/CD**: See [docs/pipeline_setup.md](docs/pipeline_setup.md)

**Automated deployments** trigger on pushes to `main` branch via GitHub Actions.

## Team

- **AWS Specialist**: Handles AWS infrastructure and deployments
- **Azure Specialist**: Manages Azure infrastructure and deployments
- **DevOps Lead**: Maintains CI/CD pipeline and monitoring
- **QA Engineer**: Ensures test coverage and quality standards

## Contributing

1. Create feature branch from `develop`
2. Make changes and add tests
3. Run test suite locally
4. Submit PR to `main` branch
5. Wait for CI checks to pass
6. Merge after review approval

---

*Built with Streamlit and Google Generative AI*
