```markdown
# Domain-Specific Testing

## LLM Domain

### Unit Tests
Location: `tests_new/unit/llm/`
- Provider-specific logic
- Response parsing
- Error handling
- Mock client behavior

### Integration Tests
Location: `tests_new/integration/llm/`
- Real API calls (requires API keys)
- End-to-end provider integration
- Rate limiting behavior

### Fixtures
- `anthropic_mock_response` - Mock API response
- `mock_anthropic_client` - Mock client object
- `anthropic_test_prompts` - Standard test prompts

## NER Domain

### Unit Tests
Location: `tests_new/unit/ner/`
- Entity extraction logic
- Label mapping
- Edge case handling

### Integration Tests
Location: `tests_new/integration/ner/`
- Pipeline integration
- Model loading
- Training workflows

### Fixtures
- `raw_sentences` - Plain text samples
- `annotated_sentences` - Pre-labeled data
- `sample_organizations` - Entity examples

## Symbolic Domain

### Unit Tests
Location: `tests_new/unit/symbolic/`
- Formula parsing
- Expression evaluation
- Validation logic

### Integration Tests
Location: `tests_new/integration/symbolic/`
- Formula execution pipeline
- Complex calculations
- Error propagation

### Fixtures
- `basic_formulas` - Simple arithmetic
- `financial_formulas` - Finance calculations
- `invalid_formulas` - Error test cases
