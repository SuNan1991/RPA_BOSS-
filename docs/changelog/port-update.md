# Port Configuration Update

## 📝 Updated Ports

### New Port Configuration
- **Backend**: Port `3000` (was: 8000/8001)
- **Frontend**: Port `5678` (was: 5173)

## 🔧 Modified Files

### Backend Configuration
1. `backend/app/core/config.py` - Changed default PORT from 8000 to 3000
2. `backend/.env.example` - Updated PORT and CORS_ORIGINS

### Frontend Configuration
1. `frontend/vite.config.ts` - Changed port from 5173 to 5678, proxy target from 8000 to 3000
2. `frontend/src/components/LogViewer.vue` - Updated WebSocket URL to port 3000
3. `frontend/src/composables/useWebSocket.ts` - Updated WebSocket URL to port 3000

### Batch Scripts
1. `kill_all.bat` - Updated all port references to 3000 and 5678
2. `kill_all_quick.bat` - Updated all port references to 3000 and 5678
3. `restart_all.bat` - Updated backend port to 3000, frontend to 5678
4. `start_all.bat` - Updated port checks and startup commands

## 🚀 How to Start

### Using Batch Scripts (Recommended)
```bash
# Restart all services
restart_all.bat

# Or start without cleanup
start_all.bat
```

### Manual Start
```bash
# Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 3000

# Frontend
cd frontend
npm run dev
```

## 🌐 Service URLs

After starting, services will be available at:
- **Backend API**: http://localhost:3000
- **API Docs**: http://localhost:3000/docs
- **Frontend UI**: http://localhost:5678
- **Log Stats**: http://localhost:3000/api/logs/stats
- **WebSocket (Logs)**: ws://localhost:3000/ws/logs
- **WebSocket (Auth)**: ws://localhost:3000/api/auth/ws

## ⚠️ Important Notes

1. **Proxy Configuration**: Vite proxy is configured to forward `/api` requests to `http://localhost:3000`
2. **CORS**: Backend CORS is configured to allow requests from `http://localhost:5678`
3. **WebSocket**: Both WebSocket connections now point to port 3000

## 🔍 Troubleshooting

### Port Already in Use
If you get port conflicts:
```bash
# Kill all processes
kill_all.bat

# Or quick kill
kill_all_quick.bat
```

### Check Port Usage
```bash
# Check if ports are in use
netstat -ano | findstr ":3000.*LISTEN"
netstat -ano | findstr ":5678.*LISTEN"
```

## 📊 Migration Notes

If you have existing processes running on old ports:
1. Stop all existing processes
2. Run `kill_all.bat` to clean up
3. Start services with new port configuration

## 🎯 Why These Ports?

- **3000**: Standard convention for Node.js/Express backends (easier to remember)
- **5678**: Less common port, reduces conflicts with other development tools
