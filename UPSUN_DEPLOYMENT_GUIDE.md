# 🚀 Upsun Deployment Guide - TrackFutura

## ✅ Issues Fixed

### 1. **Configuration Structure Error**
- **Problem**: `variables.yaml` top-level keys must be one of applications, services or routes. Found 'variables'
- **Solution**: Integrated variables into main `config.yaml` file under applications section
- **Result**: Clean single configuration file structure

### 2. **Missing Routes Configuration**
- **Problem**: No routes configuration was detected, a single default route will be deployed
- **Solution**: Added comprehensive routes configuration with proper caching and redirects
- **Result**: Optimized routing with static file caching and www redirect

### 3. **Security Issues Resolved**
- **Problem**: Exposed API tokens in codebase triggering GitHub push protection
- **Solution**: Removed all hardcoded tokens, reset git history to clean state
- **Result**: Clean repository ready for deployment

## 📋 Current Configuration

### Project Details
- **Upsun Project ID**: `inhoolfrqniuu`
- **Application URL**: `https://main-bvxea6i-inhoolfrqniuu.upsun.app`
- **Console URL**: `https://console.upsun.com/projects/inhoolfrqniuu`

### Fixed Configuration Files

#### `.upsun/config.yaml`
```yaml
applications:
  backend:
    source:
      root: backend
    type: python:3.12
    size: S
    
    # Optimized build process
    build:
      flavor: none
    
    # Enhanced build hooks
    hooks:
      build: |
        set -e
        echo "🚀 Starting TrackFutura Upsun build..."
        pip install --upgrade pip
        pip install -r requirements.txt
        export DJANGO_SETTINGS_MODULE=config.settings_upsun
        python manage.py collectstatic --noinput --clear --verbosity=2
        python manage.py migrate --noinput --verbosity=2
        echo "✅ Build completed successfully!"
    
    # High-performance web configuration
    web:
      commands:
        start: "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --worker-class sync --preload --log-level info --access-logfile - --error-logfile -"
      locations:
        "/":
          passthru: true
          scripts: true
        "/static":
          root: "staticfiles"
          expires: 86400  # 24h cache
          passthru: false
        "/media":
          root: "media"
          expires: 3600   # 1h cache
          passthru: false

# Services
services:
  postgresql:
    type: postgresql:15
    size: S
    disk: 1024
    configuration:
      max_connections: 100

# Routes with proper caching
routes:
  "https://{default}/":
    type: upstream
    upstream: "backend:http"
    cache:
      enabled: true
      default_ttl: 0
      cookies: ["*"]
      headers: ["Authorization"]

  "https://www.{default}/":
    type: redirect
    to: "https://{default}/"

  "https://{default}/static/":
    type: upstream  
    upstream: "backend:http"
    cache:
      enabled: true
      default_ttl: 86400  # 24 hours for static files

  "https://{default}/media/":
    type: upstream
    upstream: "backend:http" 
    cache:
      enabled: true
      default_ttl: 3600   # 1 hour for media files
```

#### `backend/config/settings_upsun.py`
- **Optimized for project inhoolfrqniuu**
- **Enhanced security headers** (HSTS, secure cookies, CSRF protection)
- **Project-specific CSRF origins**
- **Proper PostgreSQL configuration** with PLATFORM_RELATIONSHIPS parsing
- **WhiteNoise static file handling**
- **Comprehensive logging setup**

## 🚀 Deployment Steps

### Option 1: Automated Script (Recommended)

#### Windows (PowerShell):
```powershell
.\deploy_upsun.ps1
```

#### Linux/macOS:
```bash
chmod +x deploy_upsun.sh
./deploy_upsun.sh
```

### Option 2: Manual Deployment

1. **Install Upsun CLI**:
   ```bash
   curl -f https://cli.upsun.com/installer | sh
   ```

2. **Login to Upsun**:
   ```bash
   upsun auth:login
   ```

3. **Set Project Context**:
   ```bash
   upsun project:set-default inhoolfrqniuu
   ```

4. **Deploy**:
   ```bash
   upsun push --yes
   ```

## ⚙️ Post-Deployment Configuration

### Required Environment Variables
Access the [Upsun Console](https://console.upsun.com/projects/inhoolfrqniuu) and set:

1. **Navigate to**: Environment > Variables
2. **Add variables**:
   - `APIFY_API_TOKEN`: Your Apify API token
   - `OPENAI_API_KEY`: Your OpenAI API key

### Application URLs
- **Main Application**: https://main-bvxea6i-inhoolfrqniuu.upsun.app
- **API Endpoints**: https://main-bvxea6i-inhoolfrqniuu.upsun.app/api/
- **Admin Panel**: https://main-bvxea6i-inhoolfrqniuu.upsun.app/admin/

## 🔧 Performance Features

### Optimizations Implemented
- **2 Gunicorn workers** for better concurrency
- **Static file caching** (24 hours)
- **Media file caching** (1 hour)  
- **Compressed static files** via WhiteNoise
- **Database connection pooling**
- **Enhanced security headers**

### Resource Allocation
- **Application Size**: S (Small)
- **Database**: PostgreSQL 15, 1GB disk, 100 max connections
- **Python Version**: 3.12
- **Deployment Strategy**: Zero-downtime rolling updates

## 🛡️ Security Features

### Enhanced Security Headers
- HSTS (Strict Transport Security)
- XSS Protection
- Content Type Sniffing Protection
- Secure Cookies
- CSRF Protection

### Project-Specific Configuration
- CSRF origins configured for `inhoolfrqniuu.upsun.app`
- Proper CORS settings for API access
- Session security hardening

## 📊 Monitoring & Logs

### Access Logs
- **Upsun Console**: https://console.upsun.com/projects/inhoolfrqniuu
- **Real-time logs**: `upsun log --tail`
- **Application logs**: Available in console under Logs section

### Health Monitoring
- Application health automatically monitored by Upsun
- Database performance metrics available in console
- Request/response metrics and error tracking

## 🎯 Next Steps

1. **Deploy the application** using one of the methods above
2. **Set environment variables** in the Upsun console
3. **Test the deployment** at the provided URL
4. **Monitor logs** for any issues
5. **Configure custom domain** if needed

## ✅ Benefits Over Render Emergency Deployment

- **Better Performance**: 2 workers vs 1, professional infrastructure
- **Enhanced Security**: Comprehensive security headers and HTTPS
- **Better Caching**: Optimized static file delivery
- **Professional Database**: PostgreSQL vs SQLite
- **Zero-Downtime Deployments**: Rolling updates
- **Better Monitoring**: Comprehensive logging and metrics

---

**Success!** Your Upsun configuration is now optimized and ready for deployment to project `inhoolfrqniuu`.