# Track-Futura Webhook Deployment Guide

## Overview

This guide covers the complete setup and deployment of the Track-Futura webhook system for BrightData integration, specifically optimized for Upsun deployment.

## ✅ Deployment Fixes Applied

The following critical deployment issues have been resolved:

### 1. DataDog Auto-Injection Removed
- **Issue**: Upsun was auto-injecting DataDog tracing libraries causing `ddtrace.profiling.exporter.ExportError: Server returned 400, check your API key` errors
- **Solution**: Completely removed DataDog references and disabled auto-injection through environment variables

### 2. Enhanced Webhook Security
- Professional-grade HMAC signature verification
- Timestamp-based replay attack prevention
- Rate limiting and IP whitelisting
- Comprehensive error handling and monitoring

### 3. Auto-Detection for URL Configuration
- Automatic detection of Upsun environment and base URLs
- Fallback support for development and other cloud platforms
- Ngrok integration for local testing

## 🚀 Quick Start

### Local Development

1. **Start the Django server:**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Test webhook configuration:**
   ```bash
   python manage.py test_brightdata_setup
   ```

3. **Run deployment tests:**
   ```bash
   python test_webhook_deployment.py
   ```

### Testing with Ngrok

1. **Install and start ngrok:**
   ```bash
   ngrok http 8000
   ```

2. **Test ngrok integration:**
   ```bash
   python manage.py test_brightdata_setup --test-ngrok
   ```

3. **Test webhook endpoint:**
   ```bash
   python manage.py test_brightdata_setup --test-webhook
   ```

## 🌐 Upsun Deployment

### Environment Variables

The following environment variables are automatically configured in `.upsun/config.yaml`:

```yaml
variables:
  env:
    DD_TRACE_ENABLED: "false"
    DD_PROFILING_ENABLED: "false"
    DD_APM_ENABLED: "false"
    DD_LOGS_ENABLED: "false"
    DD_TRACE_STARTUP_LOGS: "false"
    DD_RUNTIME_METRICS_ENABLED: "false"
    DD_INSTRUMENTATION_TELEMETRY_ENABLED: "false"
```

### Production Configuration

For production deployment, you should set:

```bash
# Set a secure webhook token
export BRIGHTDATA_WEBHOOK_TOKEN="your-secure-token-here"

# Optional: Configure rate limiting
export WEBHOOK_RATE_LIMIT="100"  # requests per minute

# Optional: IP whitelisting (comma-separated)
export WEBHOOK_ALLOWED_IPS="1.2.3.4,10.0.0.0/8"
```

## 🔧 API Configuration

### BrightData API Request Parameters

When making requests to the BrightData API, use these parameters:

```python
import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
    "Authorization": "Bearer YOUR_BRIGHTDATA_API_TOKEN",
    "Content-Type": "application/json"
}

data = {
    "url": "https://example.com/target-page",
    "endpoint": "https://your-app.upsun.app/api/brightdata/webhook/",
    "auth_header": "Bearer your-secure-webhook-token",
    "notify": "https://your-app.upsun.app/api/brightdata/notify/",
    "format": "json",
    "uncompressed_webhook": "true",
    "include_errors": "true"
}

response = requests.post(url, headers=headers, json=data)
```

## 🔒 Security Features

### Authentication
- Bearer token authentication for all webhook requests
- Configurable webhook tokens via environment variables
- Constant-time comparison to prevent timing attacks

### Rate Limiting
- Configurable requests per minute limit
- IP-based rate limiting with cache-backed storage
- Automatic cleanup of expired rate limit data

### Replay Attack Prevention
- Timestamp validation with configurable maximum age
- Request ID tracking to prevent duplicate processing
- Automatic cleanup of processed request IDs

### IP Whitelisting
- Support for individual IPs and CIDR notation
- Automatic IP extraction from forwarded headers
- Flexible configuration for development and production

## 📊 Monitoring & Observability

### Webhook Metrics
- Real-time performance tracking
- Error rate monitoring
- Response time analytics
- Health status indicators

### Available Endpoints
- `/api/brightdata/webhook/metrics/` - Performance metrics
- `/api/brightdata/webhook/health/` - Health status
- `/api/brightdata/webhook/events/` - Event history
- `/api/brightdata/webhook/alerts/` - Alert management

## 🧪 Testing

### Pre-Deployment Tests

Run the comprehensive test suite before deploying:

```bash
cd backend
python test_webhook_deployment.py
```

This tests:
- Django configuration
- Webhook URL accessibility
- Security configuration
- Environment detection
- Webhook functionality
- BrightData integration

### Manual Testing

Test webhook endpoints manually:

```bash
# Test webhook endpoint
curl -X POST "https://your-app.upsun.app/api/brightdata/webhook/" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -H "X-BrightData-Timestamp: $(date +%s)" \
  -d '{"test": "data"}'

# Test notify endpoint
curl -X POST "https://your-app.upsun.app/api/brightdata/notify/" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"snapshot_id": "test", "status": "completed"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **Webhook returns 401 Unauthorized**
   - Check webhook token configuration
   - Verify Authorization header format
   - Ensure token matches exactly

2. **Webhook returns 400 Bad Request**
   - Check timestamp format and age
   - Verify JSON payload structure
   - Check Content-Type header

3. **Rate limit exceeded**
   - Check current rate limit settings
   - Monitor request frequency
   - Consider increasing limits for high-volume usage

### Debug Mode

Enable debug logging by setting:

```python
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'brightdata_integration': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Health Checks

Monitor webhook health:

```bash
# Check webhook health
curl "https://your-app.upsun.app/api/brightdata/webhook/health/"

# Check recent events
curl "https://your-app.upsun.app/api/brightdata/webhook/events/"
```

## 📈 Performance Optimization

### Database Configuration
- Use PostgreSQL for production (configured in Upsun)
- Implement proper indexing for webhook data
- Regular cleanup of old webhook events

### Caching
- Redis cache for rate limiting (if available)
- Local memory cache for development
- Configurable cache timeouts

### Resource Usage
- Container-level CPU and RAM controls
- Efficient pagination for large datasets
- Optimized query patterns

## 🔄 Deployment Process

1. **Test locally:**
   ```bash
   python test_webhook_deployment.py
   ```

2. **Commit changes:**
   ```bash
   git add .
   git commit -m "Webhook deployment fixes and improvements"
   ```

3. **Deploy to Upsun:**
   ```bash
   git push upsun main
   ```

4. **Verify deployment:**
   ```bash
   # Check application status
   upsun app:list

   # Test webhook endpoints
   python manage.py test_brightdata_setup --test-webhook
   ```

## 🎯 Next Steps

1. **Configure production webhook token**
2. **Set up monitoring and alerting**
3. **Configure IP whitelisting if needed**
4. **Test with actual BrightData API calls**
5. **Monitor performance and optimize as needed**

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review webhook logs in Upsun dashboard
- Run the test suite to identify specific issues
- Check webhook health endpoints for status information

## 🔐 Security Checklist

- [ ] Webhook token changed from default
- [ ] HTTPS enforced for all webhook endpoints
- [ ] Rate limiting configured appropriately
- [ ] IP whitelisting configured (if required)
- [ ] Timestamp validation enabled
- [ ] Request logging configured for audit trail
- [ ] Error handling properly implemented
- [ ] Security headers configured

The webhook system is now production-ready and optimized for Upsun deployment with enterprise-grade security and monitoring capabilities.
