# 🚀 Unified Formula API - Setup Checklist

## 📁 File Structure Verification

Verify your backend directory structure matches this:

```
backend/
├── app.py                          ✅ (refactored version)
├── config.py
├── requirements.txt
│
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── ner_routes.py          ✅ (already have)
│   │   ├── defi_routes.py         ✅ (already have)
│   │   ├── agents.py              (optional)
│   │   └── models.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── ner_schemas.py         ✅
│   │   └── defi_schemas.py        ✅
│   └── middleware/
│       └── __init__.py
│
├── services/
│   ├── __init__.py
│   ├── ner_service.py             (required for NER routes)
│   └── defi_calculator.py         ✅ (already have)
│
├── logs/
│   └── app.log                    (auto-created)
│
└── test_api.py                     ✅ (new test script)
```

---

## ✅ Required Imports Check

### 1. **Check `ner_routes.py` imports**

Your `ner_routes.py` requires:

- ✅ `NERService` from `services.ner_service`
- ✅ Schemas from `api.schemas.ner_schemas`

**Action needed:** Verify `services/ner_service.py` exists and has `NERService` class

### 2. **Check `defi_routes.py` imports**

Your `defi_routes.py` requires:

- ✅ `DeFiCalculator` from `services.defi_calculator` (you have this!)

---

## 🔧 Blueprint Registration Status

In your new `app.py`, these blueprints are registered:

### ✅ NER Blueprint

```python
from api.routes.ner_routes import ner_bp
app.register_blueprint(ner_bp)
```

- URL prefix: `/api/ner` (defined in `ner_routes.py`)
- Endpoints: 9 routes available

### ✅ DeFi Blueprint

```python
from api.routes.defi_routes import defi_bp
app.register_blueprint(defi_bp)
```

- URL prefix: `/api/defi` (defined in `defi_routes.py`)
- Endpoints: 4 routes available

### ⚠️ Agents Blueprint (Optional)

```python
from api.routes.agents import agents_bp
app.register_blueprint(agents_bp)
```

- Status: Optional - will skip if not found
- No action needed unless you want agent functionality

---

## 🚦 Service Loading Status

### HypatiaX (Tableau NER)

- **Status in app.py:** Loads models from `../hypatiax/`
- **Fallback:** Demo mode with mock functions
- **Endpoints:** `/api/hypatiax/map`, `/api/hypatiax/test`, `/api/hypatiax/batch`

### NER Service

- **Status in app.py:** Tries to load from `services.ner_service`
- **Required for:** `/api/ner/*` endpoints to work
- **Action:** Check if `services/ner_service.py` exists

### DeFi Calculator

- **Status in app.py:** Loads from `services.defi_calculator`
- **Status:** ✅ You already have this file!
- **Endpoints:** `/api/defi/*` routes work via blueprint

---

## 🧪 Testing Checklist

### Step 1: Start the Server

```bash
cd backend
python app.py
```

**Expected output:**

```
================================================================================
🚀 UNIFIED FORMULA API SERVER
================================================================================
📊 HypatiaX (Tableau):    ✅ Loaded  (or ⚠️  Demo Mode)
🔢 NER Service:           ✅ Loaded  (or ❌ Not Available)
💰 DeFi Calculator:       ✅ Loaded

🌐 Server: http://localhost:5000
📡 API Documentation: http://localhost:5000/
❤️  Health Check: http://localhost:5000/api/health
...
```

### Step 2: Check Health

```bash
curl http://localhost:5000/api/health
```

### Step 3: Run Test Suite

```bash
python test_api.py
```

### Step 4: Manual Tests

**Test HypatiaX:**

```bash
curl -X POST http://localhost:5000/api/hypatiax/map \
  -H "Content-Type: application/json" \
  -d '{"description": "Calculate the total of Sales", "method": "vocab"}'
```

**Test DeFi:**

```bash
curl -X POST http://localhost:5000/api/defi/calculate-il \
  -H "Content-Type: application/json" \
  -d '{"initial_price": 2000, "current_price": 2500}'
```

**Test NER:**

```bash
curl -X POST http://localhost:5000/api/ner/extract-formula \
  -H "Content-Type: application/json" \
  -d '{"text": "IL = 2*sqrt(r)/(r+1) - 1", "domain": "defi"}'
```

---

## 🐛 Common Issues & Solutions

### Issue 1: NER Routes Not Loading

**Error:** `⚠️ NER routes not available`

**Solution:**

1. Check if `services/ner_service.py` exists
2. If not, create it with a basic `NERService` class
3. Or comment out NER blueprint registration in `app.py`

### Issue 2: Import Errors

**Error:** `ModuleNotFoundError: No module named 'services'`

**Solution:**

```bash
# Make sure __init__.py exists
touch services/__init__.py
touch api/__init__.py
touch api/routes/__init__.py
```

### Issue 3: CORS Errors (from frontend)

**Solution:** Already configured in new `app.py`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        ...
    }
})
```

### Issue 4: Port Already in Use

**Error:** `Address already in use`

**Solution:**

```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port
python app.py --port 5001
```

---

## 📊 Endpoint Availability Matrix

| Endpoint Category | Status | Routes Available | Requires |
|------------------|--------|------------------|----------|
| Root & Health | ✅ Working | 2 | None |
| HypatiaX | ✅ Working | 3 | Optional models (has fallback) |
| NER | ⚠️ Depends | 9 | `services/ner_service.py` |
| DeFi | ✅ Working | 4 | `services/defi_calculator.py` ✅ |

---

## 🎯 Priority Actions

### High Priority ✅

1. ✅ Replace old `app.py` with refactored version
2. ✅ Verify `defi_calculator.py` is in `services/` folder (you have it!)
3. ✅ Run test suite with `python test_api.py`

### Medium Priority ⚠️

4. Check if `services/ner_service.py` exists
5. If missing, either create it or remove NER blueprint registration
6. Test all endpoints with your frontend

### Low Priority 💡

7. Review logs in `logs/app.log`
8. Add custom configurations in `config.py`
9. Set up agents blueprint if needed

---

## 🎉 Success Criteria

Your API is ready when:

- ✅ Server starts without errors
- ✅ Health check returns `status: online`
- ✅ At least 2 of 3 services show as loaded
- ✅ HypatiaX endpoints return formulas (production or demo mode)
- ✅ DeFi endpoints return calculations
- ✅ Frontend can connect and make requests

---

## 📞 Need Help?

If you encounter issues:

1. Check server console output
2. Review `logs/app.log`
3. Run `python test_api.py` for detailed diagnostics
4. Verify all `__init__.py` files exist in each directory
