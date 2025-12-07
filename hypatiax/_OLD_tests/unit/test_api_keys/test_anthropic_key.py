import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

try:
    client = anthropic.Anthropic(api_key=api_key)
    # Try to make a minimal request
    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=10, messages=[{"role": "user", "content": "Hi"}]
    )
    print("✅ Key is ACTIVE and WORKING")
    print(f"Response: {response.content[0].text}")
except anthropic.AuthenticationError as e:
    print("❌ Key is INVALID or REVOKED")
    print(f"Error: {e}")
except anthropic.BadRequestError as e:
    if "credit balance" in str(e).lower():
        print("✅ Key is ACTIVE but NO CREDITS")
        print(f"Error: {e}")
    else:
        print("⚠️ Other error:", e)
except Exception as e:
    print("⚠️ Unexpected error:", e)


"""
# Run the test
python test_key_status.py
`----

---

## 🔑 **Why Keys Get Revoked**

### Common Reasons:

1. **You revoked it accidentally**
   - Clicked "Revoke" button by mistake

2. **Someone else revoked it**
   - If you have team members with access
   - Shared account

3. **Anthropic revoked it**
   - Suspicious activity detected
   - Terms of service violation
   - Security issue
   - Billing problem

4. **Key expired**
   - Some organizations set expiration dates
   - Time-limited keys

5. **Account suspended**
   - Payment failed
   - Abuse detected
   - Account verification needed

---

## 📊 **Interpret Your Error**

Your original error was:
```
'Your credit balance is too low to access the Anthropic API'
"""
