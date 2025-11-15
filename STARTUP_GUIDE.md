# 🚀 Delhi Digital Twin - Quick Startup Guide

## **Step 1: Install Dependencies**

```powershell
cd "c:\Users\mohit\Desktop\visual studio\web dev\ai for climate"
npm install
python -m pip install -r requirements.txt
```

---

## **Step 2: Start Backend (Terminal 1)**

```powershell
cd "c:\Users\mohit\Desktop\visual studio\web dev\ai for climate"
python backend/app.py
```

**Expected Output:**
```
Starting Delhi Digital Twin Backend API...
* Running on http://127.0.0.1:5000
* Debug mode: on
```

✅ Check: Navigate to `http://127.0.0.1:5000/api/health` in browser - should see `{"status":"healthy","version":"1.0.0"}`

---

## **Step 3: Start Frontend (Terminal 2)**

```powershell
cd "c:\Users\mohit\Desktop\visual studio\web dev\ai for climate"
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

✅ Open: `http://localhost:5173/` in your browser

---

## **Step 4: Test Emergency Protocol Button**

1. **Open Browser DevTools** (F12)
2. **Go to Console tab**
3. **Click the "🚨 EMERGENCY PROTOCOL ALPHA" button** on the right panel
4. **Watch the console** - you should see:
   ```
   [API] Running scenario: type=emergency, zones=[1,2,3,4,5]
   [API] Response: 5 zones updated
   ```
5. **Observe the status messages:**
   - 🚨 PHASE 1: Detecting AQI anomalies...
   - 🤖 PHASE 2: Analyzing intervention strategies...
   - ⚡ PHASE 3: Deploying emergency measures...
   - ✅ COMPLETE: X lives saved | AQI reduced by Y points

---

## **🐛 Troubleshooting**

### **Error: "Backend may be offline"**
- ✅ Check that `python backend/app.py` is running in Terminal 1
- ✅ Check that the backend is on `http://127.0.0.1:5000`
- ✅ Check firewall settings aren't blocking localhost:5000

### **Button doesn't respond**
- ✅ Open DevTools Console (F12)
- ✅ Look for error messages
- ✅ Check network tab to see if `/api/run` request is being sent
- ✅ Verify axios base URL is set: `http://127.0.0.1:5000`

### **Backend crashes**
- ✅ Check that all CSV files exist in `data/` directory:
  - `data/city_zones.csv`
  - `data/traffic.csv`
  - `data/weather.csv`

### **Frontend shows "Loading..."**
- ✅ Wait 3-5 seconds for the 3D scene to load
- ✅ Check browser console for errors
- ✅ Verify `npm run dev` is still running

---

## **✨ Features to Test**

1. **Emergency Protocol Button** - Right panel, red button at bottom
2. **Zone Info** - Left panel shows real-time AQI, Energy, Heat Island
3. **3D Scene** - Drag to rotate, scroll to zoom
4. **AI Recommendations** - View policy suggestions in right panel
5. **Quick Actions** - Truck Ban, Odd-Even, Green Zone, Free Metro buttons

---

## **📊 What Happens When Emergency Protocol is Triggered**

1. **Phase 1: Detection (2 seconds)**
   - System detects high AQI levels across zones
   
2. **Phase 2: Analysis (2 seconds)**
   - AI evaluates emergency interventions
   - Calculates impact on each zone
   
3. **Phase 3: Deployment (2 seconds)**
   - Emergency measures are activated
   - All zones show AQI reduction
   - Results display: Lives saved and AQI improvement

**Total Duration:** ~8 seconds

---

## **🔧 Recent Fixes**

✅ Fixed axios base URL configuration
✅ Added proper error handling for backend offline scenario  
✅ Improved emergency protocol with 3-phase status display
✅ Backend now properly handles 'emergency' intervention type
✅ Added fallback simulation when backend is unavailable

---

## **📝 Port Configuration**

- **Frontend:** http://localhost:5173 (Vite dev server)
- **Backend:** http://127.0.0.1:5000 (Flask API)
- **Both must be running for full functionality**

