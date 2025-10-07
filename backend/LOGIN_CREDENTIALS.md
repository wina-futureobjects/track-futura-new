# TrackFutura - Login Credentials

## Server Information
- **URL:** http://localhost:8000
- **Status:** Running on all interfaces (0.0.0.0:8000)
- **Process ID:** Check with `netstat -ano | findstr :8000`

## Demo User Credentials

### Account Details
- **Username:** `demo`
- **Password:** `demo123`
- **Email:** demo@trackfutura.com
- **Auth Token:** `2c1f2d71a1d13abb5ca9743f5585bbb7122cb180`

## Other Test Accounts

### Admin Account
- **Username:** `admin`
- **Password:** (use Django admin to reset if needed)
- **Command:** `python manage.py changepassword admin`

### Test User 1
- **Username:** `test_user`
- **Password:** (needs to be set)

### Test User 2
- **Username:** `testuser`
- **Password:** (needs to be set)

## Quick Login Test

### Using cURL
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

### Expected Response
```json
{
    "token": "2c1f2d71a1d13abb5ca9743f5585bbb7122cb180",
    "user_id": 5,
    "username": "demo",
    "email": "demo@trackfutura.com"
}
```

## API Authentication

### Using Token
Include the token in your API requests:
```bash
curl http://localhost:8000/api/endpoint/ \
  -H "Authorization: Token 2c1f2d71a1d13abb5ca9743f5585bbb7122cb180"
```

## Create New User

### Using Django Shell
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create user
user = User.objects.create_user(
    username='newuser',
    email='newuser@example.com',
    password='password123'
)

# Create token
token = Token.objects.create(user=user)
print(f"Token: {token.key}")
```

### Using Management Command
```bash
python manage.py createsuperuser
```

## Troubleshooting

### If Login Fails
1. Check server is running: `netstat -ano | findstr :8000`
2. Verify user exists: `python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='demo').exists())"`
3. Check server logs for errors
4. Test with cURL to verify API endpoint

### Reset Password
```bash
python manage.py shell -c "from django.contrib.auth.models import User; user = User.objects.get(username='demo'); user.set_password('demo123'); user.save(); print('Password reset successfully')"
```

### Regenerate Token
```bash
python manage.py shell -c "from django.contrib.auth.models import User; from rest_framework.authtoken.models import Token; user = User.objects.get(username='demo'); Token.objects.filter(user=user).delete(); token = Token.objects.create(user=user); print(f'New token: {token.key}')"
```

## Frontend Access
- Open browser to: http://localhost:8000
- Use credentials: `demo` / `demo123`
- The frontend is served from the Django backend

## Important Notes
- Server is configured to accept connections from all interfaces (0.0.0.0)
- CORS is configured to allow all origins in development
- CSRF protection is disabled for API endpoints
- Authentication tokens never expire (unless manually deleted)

---
*Last Updated: October 1, 2025*
