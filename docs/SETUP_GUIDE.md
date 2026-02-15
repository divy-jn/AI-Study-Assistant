# 🚀 AI Educational Document Reasoning System - Setup Guide

## Prerequisites

### Required Software:
1. **Python 3.10+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **Ollama** - [Download](https://ollama.com/download)
4. **Git** (optional) - [Download](https://git-scm.com/)

### Hardware Requirements:
- **Minimum:** 16GB RAM, 20GB free disk space
- **Recommended:** 24GB RAM, 50GB free disk space, NVIDIA GPU with 8GB+ VRAM

---

## Installation Steps

### Step 1: Clone or Download Project
```bash
# If using Git
git clone <repository-url>
cd ai-edu-system

# OR download and extract the ZIP file
```

### Step 2: Install Ollama and Model
```bash
# Run the setup script
setup_ollama.bat

# This will:
# - Check Ollama installation
# - Download Qwen 2.5 14B model (~8GB)
# - Test the model
```

**Manual Ollama Installation:**
1. Download from https://ollama.com/download
2. Install Ollama
3. Open Command Prompt and run:
   ```bash
   ollama pull qwen2.5:14b
   ```

### Step 3: Setup Python Environment
```bash
# Run the installation script
install_dependencies.bat

# This will:
# - Create virtual environment
# - Install all Python packages
# - Install PyTorch with CUDA support
```

**Manual Installation:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 4: Configure Environment
```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your settings (optional)
notepad .env
```

**Important Settings in .env:**
- `OLLAMA_MODEL=qwen2.5:14b` - Change if using different model
- `EMBEDDING_DEVICE=cuda` - Change to `cpu` if no GPU
- `SECRET_KEY=` - Generate secure key for production

### Step 5: Initialize Database
```bash
# Activate virtual environment
venv\Scripts\activate

# Run config to create directories
python backend_config.py

# Initialize database (will be created automatically on first run)
```

### Step 6: Setup Frontend
```bash
cd frontend

# Install Node packages
npm install

# Return to root directory
cd ..
```

---

## Running the Application

### Option 1: Automated Start (Recommended)
```bash
# Run the start script
start_dev.bat
```

This will:
- Start backend server on http://localhost:8000
- Start frontend server on http://localhost:5173
- Open two separate command windows

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## Accessing the Application

- **Frontend UI:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Ollama API:** http://localhost:11434

---

## First Time Usage

1. **Register Account:**
   - Open http://localhost:5173
   - Click "Register"
   - Create your account

2. **Upload Documents:**
   - Login to your account
   - Go to "Documents" section
   - Upload your notes, marking schemes, or question papers
   - Wait for processing to complete

3. **Start Chatting:**
   - Go to "Chat" section
   - Ask questions or request specific tasks
   - Examples:
     - "Generate answer for question 1 from my marking scheme"
     - "Evaluate my answer to this question"
     - "Explain this concept from my notes"
     - "Generate 5 MCQs on this topic"

---

## Troubleshooting

### Ollama Issues

**Problem:** "Ollama is not installed"
```bash
# Solution: Install Ollama from ollama.com
# Then run: ollama pull qwen2.5:14b
```

**Problem:** "Model not found"
```bash
# Solution: Pull the model manually
ollama pull qwen2.5:14b
```

**Problem:** "Connection refused to Ollama"
```bash
# Solution: Make sure Ollama service is running
# On Windows, Ollama should start automatically
# Check if http://localhost:11434 is accessible
```

### Python Issues

**Problem:** "Module not found"
```bash
# Solution: Make sure virtual environment is activated
venv\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

**Problem:** "CUDA not available"
```bash
# Solution 1: Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Solution 2: Use CPU mode
# Edit .env: EMBEDDING_DEVICE=cpu
```

### Frontend Issues

**Problem:** "npm: command not found"
```bash
# Solution: Install Node.js from nodejs.org
```

**Problem:** "Port 5173 already in use"
```bash
# Solution: Kill the process or use different port
# Edit frontend/vite.config.js to change port
```

### Database Issues

**Problem:** "Database file not found"
```bash
# Solution: Create data directory
mkdir data

# The database will be created automatically on first run
```

### Document Processing Issues

**Problem:** "Failed to process document"
- Check if file format is supported (PDF, DOCX, TXT)
- Check file size (max 50MB by default)
- Check if ChromaDB is running properly

---

## Performance Tips

1. **GPU Acceleration:**
   - Ensure NVIDIA drivers are up to date
   - Install CUDA toolkit if not already present
   - Set `EMBEDDING_DEVICE=cuda` in .env

2. **Model Selection:**
   - For faster responses: Use `qwen2.5:7b` or `llama3.1:8b`
   - For better quality: Use `qwen2.5:14b` (recommended)
   - For maximum quality: Use `qwen2.5:32b` (requires 32GB+ RAM)

3. **Memory Management:**
   - Close unnecessary applications
   - Monitor RAM usage (Task Manager)
   - Reduce chunk size if memory issues occur

---

## Updating the System

```bash
# Activate virtual environment
venv\Scripts\activate

# Update Python packages
pip install --upgrade -r requirements.txt

# Update frontend packages
cd frontend
npm update
cd ..

# Pull latest Ollama model
ollama pull qwen2.5:14b
```

---

## Uninstalling

1. Stop all running servers (Ctrl+C in terminals)
2. Delete the project folder
3. Uninstall Ollama (optional)
4. Delete ChromaDB data folder (optional)

---

## Getting Help

- Check API documentation: http://localhost:8000/docs
- Review error logs in `logs/app.log`
- Check Ollama logs: `ollama logs`

---

## Next Steps

After successful setup:
1. Read USER_GUIDE.md for detailed usage instructions
2. Review API_DOCUMENTATION.md for API details
3. Start uploading your academic documents
4. Explore different features and capabilities

---

## Project Structure Quick Reference

```
ai-edu-system/
├── backend/          # FastAPI backend code
├── frontend/         # React frontend code
├── data/             # Database and uploads
│   ├── uploads/      # User documents
│   ├── chroma_db/    # Vector database
│   └── sqlite.db     # Main database
├── logs/             # Application logs
└── venv/             # Python virtual environment
```

---

✅ Setup complete! You're ready to use the AI Educational Document Reasoning System!
