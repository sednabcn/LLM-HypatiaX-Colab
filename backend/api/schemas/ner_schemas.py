"""
NER Validation Schemas using Marshmallow
File: backend/api/schemas/ner_schemas.py
"""

from marshmallow import Schema, ValidationError, fields, validate, validates


class FormulaExtractionSchema(Schema):
    """Schema for formula extraction requests"""

    text = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=10000),
        error_messages={"required": "Text field is required"},
    )
    domain = fields.Str(
        missing="general",
        validate=validate.OneOf(
            [
                "general",
                "defi",
                "finance",
                "physics",
                "mathematics",
                "statistics",
                "economics",
            ]
        ),
    )
    extract_variables = fields.Bool(missing=True)
    output_format = fields.Str(
        missing="json", validate=validate.OneOf(["json", "latex", "both"])
    )


class EntityRecognitionSchema(Schema):
    """Schema for entity recognition requests"""

    text = fields.Str(required=True, validate=validate.Length(min=1, max=10000))
    entity_types = fields.List(
        fields.Str(
            validate=validate.OneOf(
                ["variable", "constant", "operator", "function", "symbol", "unit"]
            )
        ),
        missing=["variable", "constant", "operator"],
    )
    include_positions = fields.Bool(missing=True)


class BatchNERSchema(Schema):
    """Schema for batch NER processing"""

    texts = fields.List(
        fields.Str(validate=validate.Length(min=1, max=10000)),
        required=True,
        validate=validate.Length(min=1, max=100),
    )
    domain = fields.Str(
        missing="general",
        validate=validate.OneOf(
            [
                "general",
                "defi",
                "finance",
                "physics",
                "mathematics",
                "statistics",
                "economics",
            ]
        ),
    )
    extract_variables = fields.Bool(missing=True)

    @validates("texts")
    def validate_texts(self, value):
        if not value:
            raise ValidationError("texts list cannot be empty")
        if len(value) > 100:
            raise ValidationError("Maximum 100 texts allowed per batch")


class ExpressionParseSchema(Schema):
    """Schema for expression parsing"""

    expression = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    output_format = fields.Str(
        missing="tree", validate=validate.OneOf(["tree", "list", "graph"])
    )
    simplify = fields.Bool(missing=False)


class LatexConversionSchema(Schema):
    """Schema for LaTeX conversion"""

    expression = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    style = fields.Str(
        missing="inline", validate=validate.OneOf(["inline", "display", "equation"])
    )
    numbered = fields.Bool(missing=False)


class SyntaxValidationSchema(Schema):
    """Schema for syntax validation"""

    expression = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    strict = fields.Bool(missing=False)
    auto_correct = fields.Bool(missing=False)


class DomainIdentificationSchema(Schema):
    """Schema for domain identification"""

    text = fields.Str(required=True, validate=validate.Length(min=1, max=10000))
    return_confidence = fields.Bool(missing=True)
    return_keywords = fields.Bool(missing=True)


# Response Schemas (for documentation/validation)


class FormulaExtractionResponseSchema(Schema):
    """Response schema for formula extraction"""

    formulas = fields.List(fields.Str())
    variables = fields.List(fields.Str())
    constants = fields.List(fields.Str())
    operators = fields.List(fields.Str())
    latex = fields.Str(allow_none=True)
    domain = fields.Str()
    confidence = fields.Float()


class EntityResponseSchema(Schema):
    """Response schema for entity recognition"""

    text = fields.Str()
    type = fields.Str()
    position = fields.List(fields.Int())
    confidence = fields.Float()


class EntitiesResponseSchema(Schema):
    """Response schema for entities list"""

    entities = fields.List(fields.Nested(EntityResponseSchema))
    total_count = fields.Int()


class ParsedExpressionResponseSchema(Schema):
    """Response schema for parsed expression"""

    parsed = fields.Dict()
    variables = fields.List(fields.Str())
    constants = fields.List(fields.Str())
    operators = fields.List(fields.Str())
    functions = fields.List(fields.Str())
    complexity = fields.Int()


class LatexConversionResponseSchema(Schema):
    """Response schema for LaTeX conversion"""

    latex = fields.Str()
    style = fields.Str()
    preview_url = fields.Str(allow_none=True)


class ValidationResponseSchema(Schema):
    """Response schema for syntax validation"""

    valid = fields.Bool()
    errors = fields.List(fields.Str())
    warnings = fields.List(fields.Str())
    suggestions = fields.List(fields.Str())
    corrected_expression = fields.Str(allow_none=True)


class DomainIdentificationResponseSchema(Schema):
    """Response schema for domain identification"""

    domain = fields.Str()
    confidence = fields.Float()
    keywords = fields.List(fields.Str())
    alternative_domains = fields.List(fields.Dict())
