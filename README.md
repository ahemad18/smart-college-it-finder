# Smart College IT Finder

An intelligent comparison tool for IT programs across Ontario colleges, powered by machine learning and AI.

## 🚀 Quick Links

- **GitHub Repository**: [ahemad18/smart-college-it-finder](https://github.com/ahemad18/smart-college-it-finder)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Frontend Build**: [College Comparison App](college-comparison-app/)
- **Backend API**: [AI System Web](ai-system-web/)

## 📋 Project Structure

```
├── ai-system-web/              # FastAPI backend
│   ├── backend/
│   │   ├── app.py             # Main FastAPI application
│   │   ├── ml_pipeline.py     # Machine learning pipeline
│   │   └── requirements.txt   # Python dependencies
│   └── frontend/              # Legacy frontend files
├── college-comparison-app/    # React + Vite frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── docs/                       # Project documentation
├── mlruns/                     # MLflow tracking
└── .github/
    └── workflows/
        └── ci-cd.yml          # GitHub Actions pipeline
```

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, CSS3
- **Backend**: FastAPI, Python 3.11
- **ML/AI**: scikit-learn, pandas, numpy, MLflow
- **Data**: CSV-based Ontario IT college programs
- **Deployment**: GitHub Pages, Render.com, Netlify
- **CI/CD**: GitHub Actions

## 🚀 Getting Started

### Local Development

**Backend:**
```bash
cd ai-system-web/backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# Backend available at http://localhost:8000
```

**Frontend:**
```bash
cd college-comparison-app
npm install
npm run dev
# Frontend available at http://localhost:5173
```

### Running Tests
```bash
# Backend tests
cd ai-system-web/backend
pytest -v

# Frontend tests
cd college-comparison-app
npm run test
```

## 📦 Deployment

### Automatic Deployment (CI/CD via GitHub Actions)
- Pushes to `main` trigger automated tests, builds, and deployment
- Frontend deploys to GitHub Pages
- Backend deploys to Render.com

### Manual Deployment

#### Frontend to Netlify:
```bash
cd college-comparison-app
npm run build
# Connect GitHub repo to Netlify dashboard
```

#### Backend to Render:
1. Create account at [render.com](https://render.com)
2. Connect GitHub repository
3. Render auto-configures from `render.yaml`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📊 Features

- ✅ Compare IT programs across Ontario colleges
- ✅ Machine learning-based program matching
- ✅ Real-time program database
- ✅ Responsive web interface
- ✅ RESTful API backend
- ✅ Automated testing and deployment

## 🔧 Environment Setup

### Backend Environment Variables
```bash
ENVIRONMENT=development
DATABASE_URL=postgresql://localhost/smart_college
API_PORT=8000
```

### Frontend Environment Variables
```bash
VITE_API_URL=http://localhost:8000
```

## 📈 CI/CD Pipeline

The GitHub Actions workflow (`/.github/workflows/ci-cd.yml`) includes:
- ✅ Python unit tests (3.9, 3.10, 3.11)
- ✅ Frontend build verification
- ✅ Code quality checks (black, flake8)
- ✅ Automatic deployment to production
- ✅ Code coverage reporting

## 📝 Documentation

- [Deployment Guide](DEPLOYMENT.md)
- [Project Overview](docs/project_overview.md)
- [Architecture Documentation](docs/architecture.md)
- [API Documentation](ai-system-web/docs/app_docs.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📞 Support

For issues, questions, or suggestions, please open an [Issue](https://github.com/ahemad18/smart-college-it-finder/issues).

---

**Last Updated**: April 2026

For deployment and production setup, see [DEPLOYMENT.md](DEPLOYMENT.md)
