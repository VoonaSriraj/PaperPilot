# Installation Notes for Windows

## Successfully Installed Packages

All required packages for PaperLens have been installed successfully.

## Package Updates for Windows Compatibility

### ChromaDB Version Update
The original `chromadb==0.4.18` requires compilation on Windows (needs Visual C++ Build Tools). 
We've updated to `chromadb>=0.4.22` which includes pre-built wheels for Windows, eliminating the need for compilation.

### Sentence-Transformers Version Update
Updated from `sentence-transformers==2.2.2` to `>=5.0.0` for compatibility with newer `huggingface_hub` versions.
The older version was trying to import deprecated functions.

### tf-keras Dependency
Added `tf-keras` as a dependency. Even though sentence-transformers uses PyTorch (not TensorFlow), 
the transformers library requires tf-keras for compatibility. This is a compatibility layer and doesn't 
mean we're using TensorFlow - we use PyTorch for all ML operations.

If you see dependency conflict warnings, these are from other projects in your Python environment (like langchain, mcp, etc.) and won't affect PaperLens functionality.

## Quick Verification

To verify installation, run:

```bash
python -c "import fastapi, chromadb, groq, sentence_transformers; print('All packages imported successfully!')"
```

## Next Steps

1. Create your `.env` file (copy from `env.example.txt` and add your Groq API key)
2. Run the backend: `uvicorn app.main:app --reload`
3. Install frontend dependencies: `cd ../frontend && npm install`
4. Run frontend: `npm run dev`

For detailed setup instructions, see `QUICKSTART.md` in the project root.

