# HypatiaX Backend API

Flask-based REST API for the HypatiaX NER system.

## Structure

```
backend/
|-- app.py              # Main Flask application
|-- config.py           # Configuration
|-- requirements.txt    # Python dependencies
|-- .env.example       # Environment variables template
|-- api/
|   |-- routes/        # API route handlers
|   |-- middleware/    # Custom middleware
|   +-- schemas/       # Request/response schemas
|-- tests/             # Unit tests
+-- logs/              # Application logs
```

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Server

```bash
python app.py
```

The server will start at `http://localhost:5000`

## API Endpoints

### Health Check

```
GET /api/health
```

Response:

```json
{
  "status": "online",
  "version": "1.0.0",
  "models_loaded": true,
  "mode": "production"
}
```

### Map Description to Formula

```
POST /api/map
Content-Type: application/json

{
  "description": "Sum of sales by year",
  "method": "vocab"
}
```

Response:

```json
{
  "success": true,
  "formula": "SUM([sales])",
  "entities": [...],
  "confidence": 0.95,
  "processing_time_ms": 45.2
}
```

### Run Test Suite

```
GET /api/test
```

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Running Tests

```bash
pytest tests/
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```bash
docker build -t hypatiax-backend .
docker run -p 5000:5000 hypatiax-backend
```

## Troubleshooting

### Models Not Loading

If models fail to load, the backend runs in **demo mode** with mock responses.

Check:

1. Model paths in `config.py`
2. spaCy models installed
3. HypatiaX package accessible

### CORS Issues

Update `CORS_ORIGINS` in `.env` to specify allowed origins.

## License

Part of the HypatiaX project.
