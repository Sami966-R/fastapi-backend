# Configuration Files Template

## Backend Configuration

### Create `.env` file in backend directory

```env
# FastAPI Configuration
PORT=8000
ENVIRONMENT=development

# Optional: Database (for future expansion)
DATABASE_URL=sqlite:///./ml_results.db

# Optional: Logging
LOG_LEVEL=INFO

# Optional: Deployment
PRODUCTION_API_URL=https://your-domain.com
```

---

## Frontend Configuration

### Create `.env.local` file in frontend directory (after Lovable builds it)

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000

# Environment
REACT_APP_ENVIRONMENT=development

# Optional: Analytics
REACT_APP_ANALYTICS_ID=
```

### For Production, Lovable will need:

```env
REACT_APP_API_BASE_URL=https://your-api.railway.app
REACT_APP_ENVIRONMENT=production
```

---

## Docker Configuration (Optional)

### If you want to containerize the backend

Create `Dockerfile` in backend directory:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run FastAPI
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
```

### Create `.dockerignore`:

```
__pycache__
*.pyc
.git
.gitignore
.env
ml_results.json
.DS_Store
venv/
```

### Build and run:

```bash
docker build -t ml-backend .
docker run -p 8000:8000 ml-backend
```

---

## Frontend Docker Configuration (Optional)

Create `Dockerfile` in frontend directory:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=builder /app/build ./build

ENV REACT_APP_API_BASE_URL=https://your-api.com

CMD ["serve", "-s", "build", "-l", "3000"]

EXPOSE 3000
```

### Create `.dockerignore`:

```
node_modules
npm-debug.log
build
.env.local
.git
.gitignore
```

---

## Procfile for Heroku/Railway

### Create `Procfile` in backend directory (already should exist):

```
web: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### For frontend on Heroku:

```
web: npm start
```

---

## GitHub Actions CI/CD (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - run: pip install -r requirements.txt
      - run: pytest
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: vercel deploy --prod
```

---

## Railway Configuration

### Create `railway.json` (if not exists):

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "python -m uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyMaxRetries": 10,
    "restartPolicyWindowSeconds": 600
  }
}
```

---

## TypeScript Configuration

If building frontend with Lovable, you may need `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

---

## Nginx Configuration (Optional)

If hosting on your own server:

```nginx
# Frontend
upstream frontend {
    server localhost:3000;
}

# Backend
upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }

    # Backend API
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Python Requirements

### `requirements.txt` (Backend)

Ensure your backend has:

```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
torch==2.1.0
torch-geometric==2.4.0
rdkit==2023.09.1
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
matplotlib==3.8.2
jupyter==1.0.0
```

Run: `pip install -r requirements.txt`

---

## Package.json (Frontend)

After Lovable builds, ensure `package.json` has:

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "recharts": "^2.10.0",
    "@radix-ui/react-dialog": "^1.1.1",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "start": "npm run dev"
  }
}
```

Run: `npm install`

---

## Git Configuration

### `.gitignore` for entire project:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
.venv

# Node
node_modules/
npm-debug.log
build/
dist/
.next/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
ml_results.json
*.db
.sqlite
```

---

## Logging Configuration

### Python Logging

Add to your FastAPI code:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Frontend Error Tracking (Optional)

```typescript
// React Error Boundary
import React from 'react';

class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Send to error tracking service
  }

  render() {
    return this.props.children;
  }
}
```

---

## Health Check Configuration

### Backend Health Endpoint

Add to `main.py`:

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
```

### Frontend Monitoring

```typescript
async function checkBackendHealth() {
  try {
    const response = await fetch(process.env.REACT_APP_API_BASE_URL + '/health');
    return response.ok;
  } catch (error) {
    console.error('Backend health check failed');
    return false;
  }
}
```

---

## Environment Variable Checklist

### Development
- [ ] `REACT_APP_API_BASE_URL=http://localhost:8000`
- [ ] Backend `PORT=8000`
- [ ] Frontend runs on port 3000

### Staging
- [ ] `REACT_APP_API_BASE_URL=https://staging-api.com`
- [ ] All endpoints verified
- [ ] Error handling tested

### Production
- [ ] `REACT_APP_API_BASE_URL=https://api.yourdomain.com`
- [ ] HTTPS enforced
- [ ] CORS restricted
- [ ] Authentication enabled
- [ ] Database configured
- [ ] Rate limiting enabled
- [ ] Monitoring active

---

## Quick Setup Commands

### Backend Setup
```bash
# Create .env file
echo "PORT=8000" > .env
echo "ENVIRONMENT=development" >> .env

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

### Frontend Setup (After Lovable build)
```bash
# Create env file
echo "REACT_APP_API_BASE_URL=http://localhost:8000" > .env.local

# Build and run
npm install
npm start
```

### Docker Setup
```bash
# Backend
docker build -t ml-backend .
docker run -p 8000:8000 ml-backend

# Frontend
docker build -t ml-frontend .
docker run -p 3000:3000 ml-frontend
```

---

**Copy these files to their respective directories and configure as needed!**
