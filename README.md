# ai-portfolio-assistant
AI-powered tool for generating professional bios, project summaries, and learning reflections.

## Setup: Virtual Environment & Dependencies

Follow these steps to create an isolated Python environment and install project dependencies from `requirements.txt`.

### Prerequisites
- Python 3.10+ installed
- Git (optional)

### Windows (PowerShell)
```powershell
# From the project root
py -m venv .venv
.\.venv\Scripts\Activate

# Upgrade pip (recommended)
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

To deactivate later:
```powershell
deactivate
```

### macOS/Linux (bash/zsh)
```bash
# From the project root
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip (recommended)
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

To deactivate later:
```bash
deactivate
```

### Notes
- If `py` is not found on Windows, try `python` instead.
- If you use a different Python version, ensure the `python`/`python3` command points to it.
