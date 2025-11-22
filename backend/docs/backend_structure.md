# Complete Backend Directory Structure

```
backend/
│
├── api/                                # API Layer
│   ├── __init__.py
│   ├── routes/                         # Route handlers
│   │   ├── __init__.py
│   │   ├── ner_routes.py              # NER endpoints (NEW)
│   │   └── defi_routes.py             # DeFi endpoints (optional)
│   │
│   ├── schemas/                        # Validation schemas
│   │   ├── __init__.py
│   │   ├── ner_schemas.py             # NER validation (NEW)
│   │   └── defi_schemas.py            # DeFi validation (optional)
│   │
│   └── middleware/                     # Middleware
│       ├── __init__.py
│       ├── auth.py                    # Authentication
│       └── cors.py                    # CORS handling
│
├── services/                           # Business Logic
│   ├── __init__.py
│   ├── ner_service.py                 # NER service (NEW)
│   └── defi_calculator.py             # DeFi calculations
│
├── defi/                              # DeFi specific modules
│   ├── __init__.py
│   └── il_calculator.py               # IL calculations
│
├── mappings/                          # LLM mappings
│   ├── __init__.py
│   └── llm_mapping.py                 # LLM mapper
│
├── validators/                        # Validators (optional)
│   ├── __init__.py
│   └── symbolic_validator.py          # Formula validator
│
├── tests/                             # Test files (NEW)
│   ├── __init__.py
│   ├── api_test_examples.sh          # Bash test script
│   ├── test_api_client.py            # Python test client
│   ├── test_ner_service.py           # NER unit tests
│   └── test_defi_calculator.py       # DeFi unit tests
│
├── logs/                              # Log files
│   └── app.log
│
├── app.py                             # Main Flask application
├── config.py                          # Configuration
├── requirements.txt                   # Python dependencies
├── .env                              # Environment variables
├── .env.example                      # Environment variables template
└── README.md                         # Documentation
```

## File Creation Steps

### Step 1: Create Directory Structure

```bash
# Navigate to backend directory
cd backend

# Create new directories
mkdir -p api/routes api/schemas api/middleware
mkdir -p services
mkdir -p tests
mkdir -p validators
mkdir -p logs

# Create __init__.py files
touch api/__init__.py
touch api/routes/__init__.py
touch api/schemas/__init__.py
touch api/middleware/__init__.py
touch services/__init__.py
touch tests/__init__.py
touch validators/__init__.py
```

### Step 2: Place Test Files

```bash
# Copy test files to tests/ directory
# Place the bash script
mv api_test_examples.sh tests/
chmod +x tests/api_test_examples.sh

# Place the Python test client
mv test_api_client.py tests/
```

### Step 3: Create NER Files

Create these files with the content I provided:
- `api/routes/ner_routes.py` (from artifact)
- `api/schemas/ner_schemas.py` (from artifact)
- `services/ner_service.py` (from artifact)

### Step 4: Update app.py

```python
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import blueprints
from api.routes.ner_routes import ner_bp

# Import services
from mappings.llm_mapping import LLMMapper
from defi.il_calculator import calculate_il_with_fees

app = Flask(__name__)
CORS(app)

# Initialize services
mapper = LLMMapper(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Register blueprints
app.register_blueprint(ner_bp)

# Keep your existing routes
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
    from validators.symbolic_validator import SymbolicValidator
    validator = SymbolicValidator()
    result = validator.validate(
        data['formula_latex'],
        data.get('domain', 'defi')
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Step 5: Update requirements.txt

```txt
flask==3.0.0
flask-cors==4.0.0
marshmallow==3.20.0
sympy==1.12
requests==2.31.0
python-dotenv==1.0.0
```

### Step 6: Install Dependencies

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

### Option 1: Bash Script

```bash
# Make executable
chmod +x tests/api_test_examples.sh

# Run tests
./tests/api_test_examples.sh
```

### Option 2: Python Client

```bash
# Run the test client
python tests/test_api_client.py
```

### Option 3: Manual cURL Tests

```bash
# Test NER - Extract Formula
curl -X POST http://localhost:5000/api/ner/extract-formula \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The impermanent loss is calculated as IL = 2*sqrt(price_ratio)/(price_ratio+1) - 1",
    "domain": "defi",
    "extract_variables": true
  }'

# Test NER - Recognize Entities
curl -X POST http://localhost:5000/api/ner/recognize-entities \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Calculate daily fees using volume V and fee rate f",
    "entity_types": ["variable", "constant", "operator"]
  }'

# Test NER - Convert to LaTeX
curl -X POST http://localhost:5000/api/ner/convert-to-latex \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "IL = 2*sqrt(r)/(r+1) - 1",
    "style": "inline"
  }'
```

## API Endpoints Summary

### NER Endpoints (NEW)
- `GET /api/ner/health` - Health check
- `POST /api/ner/extract-formula` - Extract formulas from text
- `POST /api/ner/recognize-entities` - Recognize mathematical entities
- `POST /api/ner/parse-expression` - Parse expression structure
- `POST /api/ner/convert-to-latex` - Convert to LaTeX
- `POST /api/ner/batch-extract` - Batch formula extraction
- `POST /api/ner/identify-domain` - Identify mathematical domain
- `POST /api/ner/validate-syntax` - Validate expression syntax

### Existing Endpoints
- `POST /generate` - Generate formula with LLM
- `POST /calculate-il` - Calculate impermanent loss
- `POST /validate` - Validate formula

## Environment Variables

Create `.env` file:

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

## Next Steps

1. ✅ Create directory structure
2. ✅ Place test files in `tests/`
3. ✅ Create NER modules
4. ✅ Update `app.py` to register NER blueprint
5. ✅ Install dependencies
6. ✅ Run tests to verify everything works
7. 🔄 Optionally: Create frontend integration
8. 🔄 Optionally: Add authentication middleware
9. 🔄 Optionally: Add logging and monitoring