# Track-Futura Webhook System - Production Deployment Guide

## Overview

This guide covers the complete setup and deployment of the Track-Futura webhook system for BrightData integration, including local development with ngrok and production deployment on Upsun.

## 🏗️ Architecture Overview

The webhook system consists of:

- **Django Backend**: Handles webhook endpoints with enterprise-grade security
- **BrightData Integration**: Processes scraped social media data
- **Security Layer**: HMAC authentication, rate limiting, IP whitelisting
- **Monitoring**: Real-time webhook health and performance monitoring
- **Auto-Discovery**: Automatic URL detection for different deployment environments

## 🔧 Local Development Setup

### Prerequisites

1. **Python 3.8+** with Django 5.2
2. **Node.js 18+** for frontend
3. **ngrok** for webhook testing (optional but recommended)

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd Track-Futura

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Environment setup
cp env.development.template .env
```

### Configuration

Create `.env` file in project root:

```bash
# Webhook Configuration
BRIGHTDATA_WEBHOOK_TOKEN=your-secure-webhook-token-change-this-in-production
BRIGHTDATA_BASE_URL=http://localhost:8000

# Ngrok Configuration (Optional)
NGROK_ENABLED=true
NGROK_AUTH_TOKEN=your-ngrok-auth-token
NGROK_SUBDOMAIN=your-custom-subdomain
NGROK_REGION=us

# Security Settings
WEBHOOK_RATE_LIMIT=100
WEBHOOK_MAX_TIMESTAMP_AGE=300
WEBHOOK_ALLOWED_IPS=  # Empty for development
```

### Running Locally

```bash
# Terminal 1: Start Django backend
cd backend
python manage.py runserver 8000

# Terminal 2: Start React frontend
cd frontend
npm run dev

# Terminal 3: Start ngrok (optional)
cd backend
python manage.py start_ngrok --port 8000
```

### Testing Webhooks Locally

```bash
# Test webhook system
python test_webhook_simple.py

# Test with ngrok
python manage.py test_webhook_setup --test-ngrok

# Manual webhook test
curl -X POST http://localhost:8000/api/brightdata/webhook/ \
  -H "Authorization: Bearer your-secure-webhook-token-change-this-in-production" \
  -H "Content-Type: application/json" \
  -d '{"test": true, "platform": "facebook"}'
```

## 🚀 Production Deployment (Upsun)

### Environment Variables

Set these in your Upsun environment:

```bash
# Required
BRIGHTDATA_WEBHOOK_TOKEN=your-production-webhook-token-super-secure
DJANGO_SECRET_KEY=your-django-secret-key

# Optional (auto-detected)
BRIGHTDATA_BASE_URL=  # Auto-detected from Upsun routes
WEBHOOK_RATE_LIMIT=1000
WEBHOOK_MAX_TIMESTAMP_AGE=300

# Security (Production)
WEBHOOK_ALLOWED_IPS=1.2.3.4,5.6.7.8/24  # BrightData IP ranges
WEBHOOK_ENABLE_CERT_PINNING=true
```

### Upsun Configuration

The application automatically detects Upsun environment and configures:

- **Base URL**: Auto-detected from `PLATFORM_ROUTES`
- **Database**: PostgreSQL (auto-configured)
- **Static Files**: Served via Upsun
- **HTTPS**: Enforced in production
- **CORS**: Configured for Upsun domains

### Deployment Commands

```bash
# Deploy to Upsun
upsun push

# Check deployment status
upsun environment:info

# View logs
upsun log app

# Test webhook endpoints
curl https://your-app.upsun.app/api/brightdata/webhook/health/
```

## 🔐 Security Features

### Authentication

- **HMAC Signature Verification**: SHA-256 signatures
- **Bearer Token Authentication**: Configurable tokens
- **Timestamp Validation**: Prevents replay attacks
- **Rate Limiting**: Configurable per-IP limits

### Monitoring

- **Real-time Health Checks**: `/api/brightdata/webhook/health/`
- **Performance Metrics**: Response times, success rates
- **Security Events**: Failed authentication attempts
- **Alert System**: Configurable thresholds

### IP Whitelisting

```python
# In settings.py or environment
WEBHOOK_ALLOWED_IPS = [
    '192.168.1.0/24',      # CIDR notation
    '10.0.0.1',            # Single IP
    '203.0.113.0/24'       # BrightData IP range
]
```

## 📊 BrightData Integration

### API Configuration

When creating BrightData scraping jobs, use these parameters:

```python
{
    "dataset_id": "your_dataset_id",
    "endpoint": "https://your-app.upsun.app/api/brightdata/webhook/",
    "auth_header": "Bearer your-production-webhook-token",
    "notify": "https://your-app.upsun.app/api/brightdata/notify/",
    "format": "json",
    "uncompressed_webhook": "true",
    "include_errors": "true"
}
```

### Supported Platforms

- **Facebook**: Posts, comments, pages
- **Instagram**: Posts, stories, reels, comments
- **LinkedIn**: Posts, company pages
- **TikTok**: Videos, user profiles

### Data Processing

The webhook system automatically:

1. **Validates** incoming data structure
2. **Processes** platform-specific fields
3. **Stores** data in appropriate models
4. **Updates** scraper request status
5. **Triggers** notifications

## 🧪 Testing & Monitoring

### Health Checks

```bash
# Server health
curl https://your-app.upsun.app/api/health/

# Webhook health
curl https://your-app.upsun.app/api/brightdata/webhook/health/

# Webhook metrics
curl https://your-app.upsun.app/api/brightdata/webhook/metrics/
```

### Performance Monitoring

The system tracks:

- **Request Volume**: Requests per minute/hour
- **Response Times**: Average and percentile metrics
- **Error Rates**: Failed requests and reasons
- **Security Events**: Authentication failures

### Debugging

```bash
# View webhook events
curl https://your-app.upsun.app/api/brightdata/webhook/events/

# Check alerts
curl https://your-app.upsun.app/api/brightdata/webhook/alerts/

# Test security
curl -X POST https://your-app.upsun.app/api/brightdata/webhook/test/ \
  -H "Content-Type: application/json" \
  -d '{"test_type": "security"}'
```

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check webhook token configuration
   - Verify HMAC signature generation
   - Ensure timestamp is within allowed window

2. **Rate Limiting**
   - Increase `WEBHOOK_RATE_LIMIT` setting
   - Implement exponential backoff in BrightData
   - Monitor request patterns

3. **IP Blocking**
   - Update `WEBHOOK_ALLOWED_IPS` with BrightData IPs
   - Check firewall settings
   - Verify proxy headers

4. **Data Processing Errors**
   - Check payload structure
   - Verify platform field mapping
   - Review error logs

### Logs and Debugging

```bash
# Upsun logs
upsun log app --tail

# Django logs (local)
tail -f backend/logs/webhook.log

# Security events
curl https://your-app.upsun.app/api/brightdata/webhook/events/ | jq '.security_events'
```

## 📈 Performance Optimization

### Recommended Settings

```python
# Production settings
WEBHOOK_RATE_LIMIT = 1000  # Requests per minute
WEBHOOK_MAX_TIMESTAMP_AGE = 300  # 5 minutes
WEBHOOK_MAX_EVENTS = 10000  # Event history
WEBHOOK_METRICS_RETENTION = 86400  # 24 hours
```

### Scaling Considerations

- **Database**: Use PostgreSQL with proper indexing
- **Caching**: Redis for webhook event storage
- **Load Balancing**: Multiple Upsun instances
- **CDN**: Static asset delivery

## 🔄 Maintenance

### Regular Tasks

1. **Monitor webhook health** daily
2. **Review security events** weekly
3. **Update webhook tokens** monthly
4. **Check performance metrics** continuously

### Updates

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Test webhook functionality
python test_webhook_simple.py --url https://your-app.upsun.app
```

## 📞 Support

For issues or questions:

1. Check the webhook health endpoint
2. Review application logs
3. Test with the provided scripts
4. Monitor security events

The webhook system is designed for enterprise-grade reliability and security, suitable for high-volume social media data processing.
