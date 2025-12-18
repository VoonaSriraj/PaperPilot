# Quick Start Guide - PaperLens

Get PaperLens running locally in 5 minutes!

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm installed
- Groq API key ([Get one here](https://console.groq.com/))

## Step 1: Clone and Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# Run backend (in one terminal)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at `http://localhost:8000`

## Step 2: Setup Frontend

```bash
# Open a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend will be running at `http://localhost:5173`

## Step 3: Test It Out!

1. Open `http://localhost:5173` in your browser
2. Upload a research paper PDF
3. Wait for processing (30-60 seconds for first upload)
4. Ask questions like:
   - "What is the main contribution?"
   - "Explain the methodology"
   - "Summarize the results"

## Troubleshooting

**Backend won't start?**
- Check if port 8000 is available
- Verify GROQ_API_KEY is set correctly
- Check Python version: `python --version` (should be 3.11+)

**Frontend won't connect?**
- Verify backend is running
- Check browser console for errors
- Ensure `VITE_API_URL` matches backend URL

**Upload fails?**
- Check file size (< 50MB)
- Ensure file is a valid PDF with extractable text
- Check backend logs for errors

**Slow responses?**
- First request loads embedding model (~30s)
- Groq API may have rate limits
- Large PDFs take longer to process

## Next Steps

- Read [README.md](README.md) for full documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Customize explanation levels and system prompts in backend code

Happy paper reading! 📄✨

