from marshmallow import Schema, fields, validate


class ILCalculationSchema(Schema):
    current_price = fields.Float(required=True, validate=validate.Range(min=0))
    initial_price = fields.Float(required=True, validate=validate.Range(min=0))

class PositionAnalysisSchema(Schema):
    initial_token_a = fields.Float(required=True)
    initial_token_b = fields.Float(required=True)
    initial_price = fields.Float(required=True)
    current_price = fields.Float(required=True)
    days_elapsed = fields.Integer(required=True, validate=validate.Range(min=0))
    daily_volume = fields.Float(required=True)
    pool_tvl = fields.Float(required=True)
    fee_rate = fields.Float(missing=0.003)
```

### **API Endpoints You'll Have:**
```
POST /api/defi/calculate-il
POST /api/defi/calculate-quality-score
POST /api/defi/analyze-position
GET  /api/defi/health
