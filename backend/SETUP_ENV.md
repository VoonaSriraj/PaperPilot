# Setting Up Environment Variables

The backend requires a `GROQ_API_KEY` to be set in the `.env` file.

## Steps to Set Up

1. **Get a Groq API Key:**
   - Go to https://console.groq.com/
   - Sign up or log in
   - Create an API key

2. **Create/Edit the .env file:**
   ```powershell
   cd backend
   # If .env doesn't exist, copy from template:
   copy env.example.txt .env
   ```

3. **Edit .env file:**
   Open `.env` in a text editor and replace `your_groq_api_key_here` with your actual API key:
   ```
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

4. **Verify the file is set up correctly:**
   The `.env` file should be in the `backend/` directory and look like:
   ```
   GROQ_API_KEY=gsk_your_actual_key
   CHROMA_PERSIST_DIR=./chroma_db
   RAG_TOP_K=5
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:5174
   ```

5. **Restart the server:**
   After setting the API key, restart uvicorn:
   ```powershell
   uvicorn app.main:app --reload
   ```

## Security Note

- Never commit the `.env` file to git (it's already in `.gitignore`)
- Never share your API key publicly
- The `.env` file stays on your local machine only

