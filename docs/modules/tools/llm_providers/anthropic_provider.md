# Module: `tools/llm_providers/anthropic_provider.py`

**Last Modified**: 2025-11-13T10:50:07.270823

## Dependencies

- `anthropic`
- `json`
- `pathlib`
- `typing`

## Classes

### `AnthropicProvider`

Anthropic Claude integration for formula generation

Usage:
    provider = AnthropicProvider(api_key="your-key")
    result = provider.generate_formula(requirements="...", domain="defi")

**Methods**:

- `__init__(self, api_key: Optional[str])`
  - Initialize Anthropic client
- `generate_formula(self, requirements: str, domain: str, n_candidates: int) -> List[Dict[<ast.Tuple object at 0x7fa6f888e590>]]`
  - Generate analytical formulas using Claude
- `_build_prompt(self, requirements: str, domain: str, variant: int) -> str`
  - Build generation prompt
- `_parse_response(self, content: str) -> Dict[<ast.Tuple object at 0x7fa6f861e510>]`
  - Extract JSON from response
- `refine_formula(self, formula: Dict[<ast.Tuple object at 0x7fa6f861f150>], feedback: str) -> Dict[<ast.Tuple object at 0x7fa6f85646d0>]`
  - Iteratively improve formula based on feedback
