# 🚀 Deployment Guide

## Production Deployment Options

This guide covers multiple deployment platforms for the AI Resume Builder System.

---

## 1. Railway.app (Recommended - Free Tier Available)

### Steps:

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Configure Environment Variables**
   - Go to "Variables" tab
   - Add: `GEMINI_API_KEY=your_key`
   - Add: `APP_HOST=0.0.0.0`
   - Add: `APP_PORT=8000`

4. **Configure Start Command**
   - In Settings > Deploy
   - Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

5. **Deploy**
   - Railway auto-deploys on push
   - Get your public URL from dashboard

### railway.json (optional)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

## 2. Render.com (Free Tier)

### Steps:

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect repository

3. **Configure Service**
   - Name: `resume-builder`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   - Add `GEMINI_API_KEY`
   - Render auto-sets `PORT`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment

---

## 3. Heroku

### Prerequisites:
```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli
```

### Steps:

1. **Login to Heroku**
```bash
heroku login
```

2. **Create New App**
```bash
heroku create resume-builder-app
```

3. **Set Environment Variables**
```bash
heroku config:set GEMINI_API_KEY=your_key_here
```

4. **Create Procfile**

Create `Procfile` in root:
```
web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

5. **Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

6. **Open App**
```bash
heroku open
```

---

## 4. Google Cloud Run

### Prerequisites:
```bash
# Install Google Cloud SDK
# Download from: https://cloud.google.com/sdk/docs/install
```

### Steps:

1. **Create Dockerfile**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

2. **Build and Push**
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/resume-builder
```

3. **Deploy**
```bash
gcloud run deploy resume-builder \
  --image gcr.io/PROJECT-ID/resume-builder \
  --platform managed \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=your_key
```

---

## 5. Docker (Self-Hosted)

### Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  resume-builder:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./frontend:/app/frontend
```

### Commands:

```bash
# Build image
docker build -t resume-builder .

# Run container
docker run -p 8000:8000 --env-file .env resume-builder

# Using docker-compose
docker-compose up -d
```

---

## 6. AWS Elastic Beanstalk

### Prerequisites:
```bash
# Install EB CLI
pip install awsebcli
```

### Steps:

1. **Initialize EB**
```bash
eb init -p python-3.9 resume-builder
```

2. **Create Environment**
```bash
eb create resume-builder-env
```

3. **Set Environment Variables**
```bash
eb setenv GEMINI_API_KEY=your_key
```

4. **Deploy**
```bash
eb deploy
```

5. **Open Application**
```bash
eb open
```

---

## 7. Azure App Service

### Prerequisites:
```bash
# Install Azure CLI
# Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
```

### Steps:

1. **Login to Azure**
```bash
az login
```

2. **Create Resource Group**
```bash
az group create --name resume-builder-rg --location eastus
```

3. **Create App Service Plan**
```bash
az appservice plan create --name resume-builder-plan --resource-group resume-builder-rg --sku B1 --is-linux
```

4. **Create Web App**
```bash
az webapp create --resource-group resume-builder-rg --plan resume-builder-plan --name resume-builder-app --runtime "PYTHON|3.9"
```

5. **Configure App**
```bash
az webapp config appsettings set --resource-group resume-builder-rg --name resume-builder-app --settings GEMINI_API_KEY=your_key
```

6. **Deploy**
```bash
az webapp up --name resume-builder-app --resource-group resume-builder-rg
```

---

## Environment Variables for Production

### Required:
```
GEMINI_API_KEY=your_gemini_api_key
```

### Optional:
```
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False
```

---

## Post-Deployment Checklist

- [ ] Environment variables configured
- [ ] Application starts successfully
- [ ] Home page loads
- [ ] Resume generation works
- [ ] ATS checker works
- [ ] File uploads work
- [ ] PDF/DOCX downloads work
- [ ] HTTPS enabled (if applicable)
- [ ] Custom domain configured (if needed)

---

## Monitoring & Logs

### Railway
```bash
# View logs in Railway dashboard
```

### Heroku
```bash
heroku logs --tail
```

### Docker
```bash
docker logs -f container_name
```

### Cloud Run
```bash
gcloud run services logs read resume-builder
```

---

## Performance Optimization

### 1. Enable Caching

Add to `main.py`:
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 2. Add CDN (Cloudflare)

- Point domain to deployment URL
- Enable Cloudflare proxy
- Configure cache rules

### 3. Database (if scaling)

For user data storage:
- PostgreSQL (Heroku, Railway)
- MongoDB (Atlas)
- Firebase

---

## Security Best Practices

1. **Never commit `.env` file**
2. **Use HTTPS in production**
3. **Set `DEBUG=False`**
4. **Implement rate limiting**
5. **Add CORS restrictions**
6. **Validate all inputs**
7. **Keep dependencies updated**

---

## Cost Estimation

| Platform | Free Tier | Paid Plans |
|----------|-----------|------------|
| Railway | 500 hrs/month | From $5/month |
| Render | 750 hrs/month | From $7/month |
| Heroku | No free tier | From $7/month |
| Google Cloud | $300 credit | Pay as you go |
| AWS | 12 months free | Variable |
| Azure | $200 credit | Variable |

---

## Scaling Considerations

### Vertical Scaling
- Increase RAM/CPU on platform
- Optimize Gemini API calls
- Implement caching

### Horizontal Scaling
- Multiple instances (load balancer)
- Database for session storage
- Redis for caching

---

## Backup & Recovery

### Code
- Use Git version control
- Push to GitHub/GitLab
- Tag releases

### Data
- Backup environment variables
- Document configuration
- Export user data (if applicable)

---

## Domain Setup

### Custom Domain

1. **Purchase domain** (Namecheap, GoDaddy, etc.)

2. **Configure DNS**
   - Add A record or CNAME
   - Point to deployment URL

3. **SSL Certificate**
   - Most platforms auto-provision
   - Or use Let's Encrypt

---

## Support & Troubleshooting

### Common Deployment Issues

**Build fails:**
- Check `requirements.txt`
- Verify Python version
- Review build logs

**App crashes:**
- Check environment variables
- Review application logs
- Verify port configuration

**API errors:**
- Validate Gemini API key
- Check API quotas
- Review error messages

---

## Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: |
          # Add deployment commands
```

---

**Choose the platform that best fits your needs and budget!** 🚀

For most users, **Railway.app** or **Render.com** are recommended for their simplicity and free tiers.