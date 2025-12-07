"""
Input validation for API requests
"""

from marshmallow import Schema, ValidationError, fields, validate


class HypatiaXSchema(Schema):
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    method = fields.Str(required=True, validate=validate.OneOf(["vocab", "semantic"]))


class NERSchema(Schema):
    text = fields.Str(required=True, validate=validate.Length(min=1, max=5000))
    domain = fields.Str(validate=validate.OneOf(["general", "defi", "finance", "physics"]))


class DeFiILSchema(Schema):
    initial_price = fields.Float(required=True, validate=validate.Range(min=0, min_inclusive=False))
    current_price = fields.Float(required=True, validate=validate.Range(min=0, min_inclusive=False))


class DeFiPositionSchema(Schema):
    initial_token_a = fields.Float(required=True, validate=validate.Range(min=0, min_inclusive=False))
    initial_token_b = fields.Float(required=True, validate=validate.Range(min=0, min_inclusive=False))
    initial_price = fields.Float(required=True, validate=validate.Range(min=0, min_inclusive=False))
    current_price = fields.Float(required=True, validate=validate.Range(min=0, min_inclusive=False))
    daily_volume_usd = fields.Float(required=True, validate=validate.Range(min=0))
    pool_tvl_usd = fields.Float(required=True, validate=validate.Range(min=0, min_inclusive=False))
    days_elapsed = fields.Int(required=True, validate=validate.Range(min=1))
    fee_rate = fields.Float(required=True, validate=validate.Range(min=0, max=1))


def validate_request(schema_class, data):
    """
    Validate request data against schema
    """
    schema = schema_class()
    try:
        return schema.load(data), None
    except ValidationError as err:
        return None, err.messages
