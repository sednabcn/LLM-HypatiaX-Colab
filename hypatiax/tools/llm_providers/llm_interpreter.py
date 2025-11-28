import os
from anthropic import Anthropic
from typing import Dict
from dataclasses import dataclass
import json
import re
from dotenv import load_dotenv

@dataclass
class InterpretationConfig:
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 2000
    temperature: float = 0.3

class LLMInterpreter:
    def __init__(self, config: InterpretationConfig = None):
        load_dotenv()
        self.config = config or InterpretationConfig()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=api_key)
        self.domain_templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, str]:
        return {
            'defi': """You are interpreting a DISCOVERED analytical expression from DeFi data.
Your role is INTERPRETATION, not generation.

DISCOVERED EXPRESSION: {expression}

Context:
- Domain: Decentralized Finance (DeFi)
- Variables: {variables}
- R² score: {r2:.4f}
- Discovered via symbolic regression

Provide structured analysis:
1. PHYSICAL INTERPRETATION: What does each term represent?
2. KNOWN ANALOGIES: Similar expressions in literature?
3. NOVEL ASPECTS: What is new or unexpected?
4. PREDICTIONS: What does this expression enable?
5. LIMITATIONS: Under what conditions might it fail?

CRITICAL: Respond with ONLY valid JSON, no markdown code fences, no preamble.
Format as JSON with keys: interpretation, analogies, novelty, predictions, limitations""",

            'risk': """You are interpreting a DISCOVERED analytical expression from Risk Management data.
Your role is INTERPRETATION, not generation.

DISCOVERED EXPRESSION: {expression}

Context:
- Domain: Financial Risk Management
- Variables: {variables}
- R² score: {r2:.4f}

Provide structured analysis:
1. STATISTICAL INTERPRETATION: What risk measure is this?
2. REGULATORY CONTEXT: Relevant frameworks (Basel III, SR 11-7)?
3. KNOWN FORMULAS: Similar established risk metrics?
4. PRACTICAL USE: How would risk managers apply this?
5. VALIDATION NEEDS: What additional tests required?

CRITICAL: Respond with ONLY valid JSON, no markdown code fences, no preamble.
Format as JSON with keys: interpretation, regulatory, known_formulas, practical_use, validation"""
        }
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that may contain markdown code fences."""
        # Remove markdown code fences
        text = re.sub(r'^```json\s*\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n```\s*$', '', text, flags=re.MULTILINE)
        text = text.strip()
        return text
    
    def interpret(self, expression: str, domain: str, 
                  variables: Dict, r2: float) -> Dict:
        template = self.domain_templates.get(domain, self.domain_templates['defi'])
        var_str = "\n".join([f"  - {k}: {v}" for k, v in variables.items()])
        
        prompt = template.format(
            expression=expression,
            variables=var_str,
            r2=r2
        )
        
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        
        try:
            # Clean the response text before parsing
            clean_text = self._extract_json(response_text)
            interpretation = json.loads(clean_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}...")
            interpretation = {
                'raw_text': response_text,
                'status': 'unparsed',
                'error': str(e)
            }
        
        interpretation['expression'] = expression
        interpretation['domain'] = domain
        interpretation['r2_score'] = r2
        
        return interpretation

if __name__ == "__main__":
    interpreter = LLMInterpreter()
    
    result = interpreter.interpret(
        expression="2*sqrt(price_ratio)/(price_ratio + 1) - 1",
        domain="defi",
        variables={'price_ratio': 'Current price / Initial price'},
        r2=0.98
    )
    
    # print(json.dumps(result, indent=2, ensure_ascii=False)))

    from hypatiax.tools.formatters.formatter import InterpretationFormatter

    formatter = InterpretationFormatter()
    formatter.to_rich_panel(result)  # Beautiful terminal output
