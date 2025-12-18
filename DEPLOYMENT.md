# Deployment Guide - PaperLens

This guide provides detailed instructions for deploying PaperLens to production environments.

## Prerequisites

- GitHub repository with your code
- Render account (for backend)
- Vercel account (for frontend)
- Groq API key

## Backend Deployment (Render)

### Step 1: Prepare Backend

Ensure your `backend/` directory contains:
- `requirements.txt`
- `Dockerfile` (optional, Render can auto-detect)
- `app/main.py`

### Step 2: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository containing PaperLens

### Step 3: Configure Backend Service

**Basic Settings:**
- **Name**: `paperlens-backend` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your production branch)

**Build Settings:**
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
```bash
GROQ_API_KEY=your_groq_api_key_here
CHROMA_PERSIST_DIR=/opt/render/project/src/chroma_db
RAG_TOP_K=5
CORS_ORIGINS=https://your-frontend-domain.vercel.app
PORT=10000
```

**Advanced Settings:**
- **Auto-Deploy**: `Yes` (deploys on push to main branch)
- **Health Check Path**: `/api/v1/health`

### Step 4: Deploy

Click **"Create Web Service"** and wait for deployment.

**Note:** First deployment will take 5-10 minutes as it installs dependencies including sentence-transformers.

### Step 5: Get Backend URL

After deployment, Render provides a URL like:
```
https://paperlens-backend.onrender.com
```

Use this URL for your frontend configuration.

### Render-Specific Notes

- **Free Tier Limitations**: 
  - Services spin down after 15 minutes of inactivity
  - First request may take 30+ seconds to wake up
  - Consider paid tier for production

- **Persistent Storage**:
  - ChromaDB data persists in `/opt/render/project/src/chroma_db`
  - Data persists across deployments on paid plans
  - Free tier may lose data on service recreation

## Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

Ensure your `frontend/` directory contains:
- `package.json`
- `vite.config.js`
- `index.html`

### Step 2: Import to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Select the repository

### Step 3: Configure Frontend Project

**Project Settings:**
- **Framework Preset**: `Vite`
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

**Environment Variables:**
```bash
VITE_API_URL=https://your-backend-url.onrender.com/api/v1
```

Replace `your-backend-url.onrender.com` with your actual Render backend URL.

### Step 4: Deploy

Click **"Deploy"** and wait for build to complete.

### Step 5: Get Frontend URL

Vercel provides a URL like:
```
https://paperlens-frontend.vercel.app
```

Update your backend `CORS_ORIGINS` to include this URL:
```bash
CORS_ORIGINS=https://paperlens-frontend.vercel.app
```

## Alternative: Docker Deployment

### Backend Docker Deployment

#### Build Image

```bash
cd backend
docker build -t paperlens-backend:latest .
```

#### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e CHROMA_PERSIST_DIR=/app/chroma_db \
  -v $(pwd)/chroma_db:/app/chroma_db \
  --name paperlens-backend \
  paperlens-backend:latest
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - CHROMA_PERSIST_DIR=/app/chroma_db
      - CORS_ORIGINS=http://localhost:5173
    volumes:
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

### Frontend Docker Deployment

Build frontend first:
```bash
cd frontend
npm run build
```

Then serve with nginx or another web server.

## Environment Variables Reference

### Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | - | Groq API key for LLaMA-3 |
| `CHROMA_PERSIST_DIR` | No | `./chroma_db` | ChromaDB storage path |
| `RAG_TOP_K` | No | `5` | Number of chunks to retrieve |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Allowed CORS origins |
| `PORT` | No | `8000` | Server port (Render uses `$PORT`) |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | No | `http://localhost:8000/api/v1` | Backend API URL |

## Post-Deployment Checklist

- [ ] Backend health check works: `https://your-backend.onrender.com/api/v1/health`
- [ ] Frontend connects to backend (check browser console)
- [ ] CORS is properly configured
- [ ] PDF upload works
- [ ] Chat functionality works
- [ ] All explanation levels work
- [ ] Error handling displays properly
- [ ] Environment variables are set correctly

## Monitoring and Logs

### Render Logs

View logs in Render dashboard:
1. Go to your service
2. Click **"Logs"** tab
3. View real-time logs

### Vercel Logs

View logs in Vercel dashboard:
1. Go to your project
2. Click **"Deployments"**
3. Click on a deployment
4. View build and runtime logs

## Troubleshooting

### Backend Issues

**Problem**: Service fails to start
- Check logs for missing dependencies
- Verify `GROQ_API_KEY` is set
- Ensure `start` command is correct

**Problem**: CORS errors
- Verify `CORS_ORIGINS` includes frontend URL
- Check frontend `VITE_API_URL` matches backend

**Problem**: Out of memory
- Reduce `RAG_TOP_K`
- Consider using smaller embedding model
- Upgrade Render plan

### Frontend Issues

**Problem**: Cannot connect to backend
- Verify `VITE_API_URL` is correct
- Check backend is running
- Verify CORS configuration

**Problem**: Build fails
- Check Node.js version (should be 18+)
- Verify all dependencies in `package.json`
- Check build logs for specific errors

## Scaling Considerations

### For Higher Traffic

1. **Backend**:
   - Upgrade Render plan (dedicated instance)
   - Use Redis for caching
   - Consider load balancing

2. **Vector Store**:
   - Move ChromaDB to cloud storage (S3 + EC2)
   - Use managed vector DB (Pinecone, Weaviate)

3. **Frontend**:
   - Enable Vercel CDN
   - Optimize bundle size
   - Use caching headers

### Cost Optimization

- **Free Tier**: Good for development/testing
- **Paid Plans**: Needed for production
- **Groq**: Check API pricing and rate limits
- **Render**: ~$7/month for basic production
- **Vercel**: Free tier with limitations, paid for production

## Security Best Practices

1. **Never commit** `.env` files
2. **Use environment variables** for all secrets
3. **Enable HTTPS** (automatic on Render/Vercel)
4. **Set up rate limiting** (consider Cloudflare)
5. **Validate file uploads** (already implemented)
6. **Sanitize user inputs** (already implemented)

## Support

If you encounter issues:
1. Check logs in Render/Vercel dashboards
2. Review error messages in browser console
3. Verify environment variables
4. Test locally first
5. Open an issue on GitHub

---

Happy deploying! 🚀

