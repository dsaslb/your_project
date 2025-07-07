@echo off
echo 🚀 Restaurant Management System - Development Server
echo ================================================

echo.
echo 📦 Activating virtual environment...
call venv\Scripts\activate

echo.
echo 🔧 Starting backend server (Flask)...
start "Backend Server" cmd /k "python app.py"

echo.
echo ⏳ Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo 🎨 Starting frontend server (Next.js)...
cd restaurant_frontend
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ✅ Development servers started!
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:5000
echo.
echo 💡 Press any key to stop all servers...
pause > nul

echo.
echo 🛑 Stopping servers...
taskkill /f /im python.exe > nul 2>&1
taskkill /f /im node.exe > nul 2>&1

echo.
echo 👋 Development servers stopped.
pause 