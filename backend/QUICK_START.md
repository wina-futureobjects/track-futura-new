# TrackFutura - Quick Start Guide

## After Restart

### 1. Start the Server
Double-click: `START_SERVER.bat`

OR manually:
```bash
cd C:\Users\winam\OneDrive\문서\PREVIOUS\TrackFutura\backend
python manage.py runserver 0.0.0.0:8000
```

### 2. Open Browser
Go to: **http://localhost:8000**

### 3. Login
- Username: `demo`
- Password: `demo123`

### 4. Clear Browser Cache (IMPORTANT!)
Press: **Ctrl + Shift + Delete**
Or: **Ctrl + F5** (hard refresh)

---

## If Still Not Working

### Check Server is Running
```bash
netstat -ano | findstr :8000
```
Should show: `0.0.0.0:8000` listening

### Test API Directly
```bash
curl http://localhost:8000/api/health/
```
Should return: `{"status": "healthy"...}`

### Test Login
```bash
curl -X POST http://localhost:8000/api/users/login/ -H "Content-Type: application/json" -d "{\"username\":\"demo\",\"password\":\"demo123\"}"
```

### Run Full Test Suite
```bash
python test_api_simple.py
```

---

## Troubleshooting

### Server Won't Start
1. Check if port 8000 is in use: `netstat -ano | findstr :8000`
2. Kill process: `taskkill //PID <PID> //F`
3. Start again

### Login Fails in Browser
1. **HARD REFRESH**: Ctrl + F5
2. Clear browser cache completely
3. Try in Incognito/Private mode
4. Check browser console (F12) for errors

### Connection Refused
1. Make sure server started with `0.0.0.0:8000` (not `127.0.0.1:8000`)
2. Check firewall isn't blocking port 8000
3. Try `http://127.0.0.1:8000` instead of `localhost`

---

## Files Reference
- `START_SERVER.bat` - Quick start script
- `test_api_simple.py` - API test suite
- `LOGIN_CREDENTIALS.md` - User accounts
- `SYSTEM_STATUS.md` - Full system info
- `TEST_REPORT.md` - Test results

---

**URL:** http://localhost:8000
**User:** demo
**Pass:** demo123
