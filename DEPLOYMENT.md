# Deployment Guide

This guide covers deploying the Smart College IT Finder to production.

## Overview

The project consists of:
- **Backend**: FastAPI application (Python)
- **Frontend**: React application (Vite)
- **Database**: Optional (for future scaling)
- **CI/CD**: GitHub Actions automation

## Frontend Deployment

### Option 1: GitHub Pages
1. The project is configured to deploy to GitHub Pages automatically on push to `main`
2. Set up a CNAME record (optional) for custom domain
3. Frontend builds are automatically published from `/college-comparison-app/dist`

### Option 2: Netlify
1. Connect your GitHub repository to Netlify
2. Netlify will automatically detect `netlify.toml`
3. Builds and deploys on every push to main
4. Set environment variables in Netlify dashboard:
   - `VITE_API_URL`: Backend API URL

### Option 3: Vercel
1. Import the repository to Vercel
2. Configure root directory: `college-comparison-app`
3. Build command: `npm run build`
4. Output directory: `dist`

## Backend Deployment

### Option 1: Render.com
1. Create an account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Render will detect `render.yaml` and auto-configure
4. Backend runs at: `https://smart-college-it-finder-backend.onrender.com`

**Manual Setup on Render:**
- Service name: `smart-college-it-finder-backend`
- Root directory: `ai-system-web/backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port 8000`
- Environment: Python 3.11

### Option 2: Railway.app
1. Create account at [railway.app](https://railway.app)
2. Create new project
3. Deploy from GitHub
4. Set environment variables as needed

### Option 3: Heroku (legacy - no longer free)
```bash
heroku login
heroku create smart-college-it-finder
git push heroku main
```

## Environment Variables

### Backend Requirements
```bash
# Production
DATABASE_URL=postgresql://user:pass@host/db
ENVIRONMENT=production
API_KEY=your_api_key_here
```

### Frontend Requirements
```bash
# .env files
VITE_API_URL=https://api.smart-college-it-finder.dev
```

## GitHub Actions CI/CD

The automated pipeline runs on every push and PR:

1. **Backend Tests** - Runs pytest for Python 3.9, 3.10, 3.11
2. **Frontend Build** - Builds React application with Vite
3. **Code Quality** - Runs linting with black and flake8
4. **Deploy Backend** - Auto-deploys to production on main push
5. **Deploy Frontend** - Auto-deploys to GitHub Pages on main push

**To enable automatic deployment:**

1. Add GitHub Secrets:
   ```
   RENDER_API_KEY      - Your Render API key
   RENDER_SERVICE_ID   - Your Render service ID
   ```

2. Secrets can be added at: Settings → Secrets and variables → Actions

## Local Testing Before Deployment

```bash
# Backend
cd ai-system-web/backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# Frontend
cd college-comparison-app
npm install
npm run dev
```

## Post-Deployment Checklist

- [ ] Frontend accessible at GitHub Pages URL
- [ ] Backend API responding at `/health` endpoint
- [ ] Environment variables configured in deployment platform
- [ ] CORS settings allow frontend to access backend
- [ ] Database migrations run (if applicable)
- [ ] SSL/TLS certificates configured
- [ ] Custom domain DNS records set up
- [ ] Monitoring and logging configured

## Custom Domain Setup

1. **Frontend Domain** (e.g., smart-college-it-finder.dev)
   - Point CNAME to GitHub Pages or Netlify
   - Update in `.github/workflows/ci-cd.yml` > `cname` field

2. **API Domain** (e.g., api.smart-college-it-finder.dev)
   - Point CNAME to Render.com or Railway
   - Update frontend `VITE_API_URL` environment variable

## Monitoring & Maintenance

- Check GitHub Actions logs for deployment failures
- Monitor uptime and performance via platform dashboards
- Set up error tracking (Sentry, Rollbar)
- Enable automated backups for database

## Troubleshooting

### Frontend not updating
- Clear GitHub Pages cache: Settings → Pages → Clear cache
- Rebuild manually from Actions tab

### Backend connection errors
- Verify CORS headers in `app.py`
- Check API_URL matches deployment domain
- Review environment variables in deployment platform

### Build failures
- Check Python/Node versions in GitHub Actions
- Verify `requirements.txt` and `package.json` are up-to-date
- Review build command output in Actions logs

## Documentation Links

- [Render Deployment](https://docs.render.com)
- [Netlify Deployment](https://docs.netlify.com)
- [GitHub Pages Deployment](https://docs.github.com/en/pages)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)
