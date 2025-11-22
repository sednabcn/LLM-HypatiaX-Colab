# Complete Backend Setup Guide

## 📁 Answer to Your Questions

### 1) Where to store test files?

Store them in the `tests/` directory:

```
backend/
├── tests/                          # ← CREATE THIS FOLDER
│   ├── __init__.py                # Empty file
│   ├── api_test_examples.sh       # Bash test script
│   ├── test_api_client.py         # Python API client
│   ├── test_ner_service.py        # NER unit tests
│   └── test_defi_calculator.py    # DeFi unit tests
```

### 2) NER Files Created

I've created these three files for you:
- ✅ `api/routes/ner_routes.py` - All NER API endpoints
- ✅ `api/schemas/ner_schemas.py` - Validation schemas
- ✅ `services/ner_service.py` - Core NER logic

---

## 🚀 Complete Installation Steps

### Step 1: Create Directory Structure

```bash
cd backend

# Create directories
mkdir -p api/routes api/schemas api/middleware
mkdir -p services
mkdir -p tests
mkdir -p validators
mkdir -p logs

# Create __init__.py files
touch api/__init__.py
touch api/routes/__init__.py
touch api/schemas/__init__.py
touch services/__init__.py
touch tests/__init__.py
```

### Step 2: Create All Files

#### A) Create `api/routes/ner_routes.py`
Copy the content from the **ner_routes** artifact I created.

#### B) Create `api/schemas/ner_schemas.py`
Copy the content from the **ner_schemas** artifact I created.

#### C) Create `services/ner_service.py`
Copy the content from the **ner_service** artifact I created.

#### D) Create test files in `tests/`
- Copy **api_test_examples.sh** → `tests/api_test_examples.sh`
- Copy **test_api_client.py** → `tests/test_api_client.py`
- Copy **test_ner_service.py** → `tests/test_ner_service.py`

```bash
# Make bash script executable
chmod +x tests/api_test_examples.sh
```

### Step 3: Update `app.py`

Replace or update your `app.py`:

```python
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import blueprints
from api.routes.ner_routes import ner_bp

# Import existing services
from mappings.llm_mapping import LLMMapper
from defi.il_calculator import calculate_il_with_fees

app = Flask(__name__)
CORS(app)

# Initialize services
mapper = LLMMapper(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Register blueprints
app.register_blueprint(ner_bp)  # NEW: Register NER routes

# Your existing routes
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/generate', methods=['POST'])
def generate_formula():
    data = request.json
    result = mapper.map(
        query=data['requirements'],
        domain=data.get('domain', 'defi')
    )
    return jsonify(result)

@app.route('/calculate-il', methods=['POST'])
def calculate_il():
    data = request.json
    result = calculate_il_with_fees(**data)
    return jsonify(result)

@app.route('/validate', methods=['POST'])
def validate_formula():
    data = request.json
    try:
        from validators.symbolic_validator import SymbolicValidator
        validator = SymbolicValidator()
        result = validator.validate(
            data['formula_latex'],
            data.get('domain', 'defi')
        )
        return jsonify(result)
    except ImportError:
        return jsonify({'error': 'Validator not available'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
```

### Step 4: Update `requirements.txt`

Add these dependencies:

```txt
flask==3.0.0
flask-cors==4.0.0
marshmallow==3.20.0
sympy==1.12
requests==2.31.0
python-dotenv==1.0.0
anthropic==0.7.0
```

### Step 5: Install Dependencies

```bash
# Activate virtual environment (if using)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install/update dependencies
pip install -r requirements.txt
```

### Step 6: Create `.env` File

Create `.env` in backend root:

```bash
# API Keys
ANTHROPIC_API_KEY=your_api_key_here

# Flask Config
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## ✅ Testing Everything

### Test 1: Start the Server

```bash
cd backend
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Test 2: Health Check

```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/ner/health
```

### Test 3: Run Bash Tests

```bash
cd tests
./api_test_examples.sh
```

### Test 4: Run Python Client

```bash
cd tests
python test_api_client.py
```

### Test 5: Run Unit Tests

```bash
cd tests
python test_ner_service.py
# or with pytest
pytest test_ner_service.py -v
```

### Test 6: Manual API Tests

```bash
# Test NER - Extract Formula
curl -X POST http://localhost:5000/api/ner/extract-formula \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The impermanent loss formula is IL = 2*sqrt(r)/(r+1) - 1",
    "domain": "defi",
    "extract_variables": true
  }'

# Test NER - Convert to LaTeX
curl -X POST http://localhost:5000/api/ner/convert-to-latex \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "IL = 2*sqrt(r)/(r+1) - 1",
    "style": "inline"
  }'

# Test NER - Identify Domain
curl -X POST http://localhost:5000/api/ner/identify-domain \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Calculate impermanent loss in liquidity pool"
  }'
```

---

## 📊 All Available Endpoints

### NER Endpoints (NEW)
```
GET  /api/ner/health               - Health check
POST /api/ner/extract-formula      - Extract formulas from text
POST /api/ner/recognize-entities   - Recognize mathematical entities
POST /api/ner/parse-expression     - Parse expression structure
POST /api/ner/convert-to-latex     - Convert to LaTeX format
POST /api/ner/batch-extract        - Batch formula extraction
POST /api/ner/identify-domain      - Identify mathematical domain
POST /api/ner/validate-syntax      - Validate expression syntax
```

### Your Existing Endpoints
```
GET  /health                       - API health check
POST /generate                     - Generate formula with LLM
POST /calculate-il                 - Calculate impermanent loss
POST /validate                     - Validate formula
```

---

## 🔧 Troubleshooting

### Issue: Import Errors

```bash
# Make sure all __init__.py files exist
touch api/__init__.py
touch api/routes/__init__.py
touch api/schemas/__init__.py
touch services/__init__.py
```

### Issue: Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific packages
pip install flask flask-cors marshmallow sympy
```

### Issue: CORS Errors

Update `app.py`:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
```

### Issue: Port Already in Use

```bash
# Change port in app.py
app.run(debug=True, port=5001)  # Use different port

# Or kill process on port 5000
lsof -ti:5000 | xargs kill -9  # Mac/Linux
```

---

## 📝 Final Checklist

- [ ] Created `tests/` directory
- [ ] Copied all test files to `tests/`
- [ ] Created `api/routes/ner_routes.py`
- [ ] Created `api/schemas/ner_schemas.py`
- [ ] Created `services/ner_service.py`
- [ ] Updated `app.py` to register NER blueprint
- [ ] Updated `requirements.txt`
- [ ] Created `.env` file
- [ ] Installed dependencies
- [ ] Server starts without errors
- [ ] Health checks pass
- [ ] All tests pass

---

## 🎯 Next Steps

1. **Frontend Integration**: Create React/Vue components to call these APIs
2. **Authentication**: Add JWT/API key authentication
3. **Database**: Add PostgreSQL for storing formulas
4. **Caching**: Add Redis for formula caching
5. **Monitoring**: Add logging and error tracking
6. **Documentation**: Generate OpenAPI/Swagger docs
7. **Deployment**: Deploy to AWS/Heroku/Vercel

---

## 📚 Quick Reference

### Project Structure
```
backend/
├── api/routes/        # API endpoints
├── api/schemas/       # Request validation
├── services/          # Business logic
├── tests/            # Test files HERE
├── defi/             # DeFi calculations
├── mappings/         # LLM mappings
├── app.py            # Main application
└── requirements.txt  # Dependencies
```

### Key Commands
```bash
# Start server
python app.py

# Run tests
./tests/api_test_examples.sh
python tests/test_api_client.py
python tests/test_ner_service.py

# Install packages
pip install -r requirements.txt
```

---

You now have a complete backend with:
- ✅ NER formula extraction
- ✅ DeFi calculations
- ✅ Comprehensive testing
- ✅ Organized structure
- ✅ API documentation

Ready to build! 🚀