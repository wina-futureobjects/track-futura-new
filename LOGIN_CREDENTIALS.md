# Track-Futura Login Credentials

This document contains the login credentials for development and testing purposes.

## Demo User Account
- **Username:** `demo`
- **Password:** `demo123`
- **Email:** `demo@trackfutura.com`
- **Role:** Regular User

## Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** (empty)
- **Role:** Administrator

## How to Create/Reset Demo Credentials

If you need to create or reset the demo user credentials, run:

```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py create_demo_user
```

This command will:
- Create a demo user if it doesn't exist
- Reset the demo user password to `demo123`
- Reset the admin user password to `admin123`
- Ensure proper user profiles and roles are created

## Testing Login

You can test the login functionality using curl:

```bash
# Test demo user
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# Test admin user
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Both should return a 200 status with a JSON response containing:
- `token`: Authentication token
- `user_id`: User ID
- `username`: Username
- `email`: User email
- `first_name`: First name
- `last_name`: Last name

## Troubleshooting Login Issues

If you encounter login errors:

1. **HTTP 400 "Unable to log in with provided credentials"**
   - Check that you're using the correct username and password
   - Run the `create_demo_user` command to reset credentials

2. **HTTP 500 "Empty response from server"**
   - Check backend logs: `docker-compose -f docker-compose.dev.yml logs backend`
   - Ensure the backend service is running: `docker-compose -f docker-compose.dev.yml ps`

3. **Connection refused errors**
   - Ensure Docker containers are running: `docker-compose -f docker-compose.dev.yml up -d`
   - Check that backend is accessible: `curl http://localhost:8000/api/health/`

## Security Note

⚠️ **These are development credentials only!**

Never use these credentials in production. In production:
- Use strong, unique passwords
- Enable proper authentication mechanisms
- Consider using environment variables for admin credentials
- Implement proper user management workflows
