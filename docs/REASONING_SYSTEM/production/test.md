# Install FastAPI

pip install fastapi uvicorn pydantic

# Run

cd api
python main.py

# Test

curl -X POST <http://localhost:8000/defi/impermanent-loss> \
  -H "Content-Type: application/json" \
  -d '{"price_ratio": 2.0}'

# Should return

# {

# "impermanent_loss": -0.0572

# "percentage": -5.72

# "interpretation": "At 2.0x price change, LP loses 5.72% vs holding"

# "formula_used": "2*sqrt(p)/(p+1) - 1"

# }
