# Anthropic API Credits Guide

## 🎯 Quick Summary
- **Problem**: Your API key works, but your account needs credits to make requests
- **Solution**: Add credits through Anthropic Console
- **Cost**: Pay-as-you-go or monthly subscription

---

## 📝 Step-by-Step: How to Add Credits

### Step 1: Go to Anthropic Console
1. Open your browser and go to: **https://console.anthropic.com**
2. Log in with your account credentials

### Step 2: Navigate to Plans & Billing
1. Click on your **profile/account icon** (usually top-right corner)
2. Select **"Settings"** or **"Plans & Billing"**
3. Or go directly to: **https://console.anthropic.com/settings/plans**

### Step 3: Add Credits

#### Option A: Buy Credits (Pay-as-you-go)
1. Click **"Add Credits"** or **"Purchase Credits"**
2. Choose an amount:
   - **$5** - Good for testing (~2.5M input tokens)
   - **$20** - Light development
   - **$50+** - Regular usage
3. Enter payment information
4. Confirm purchase

#### Option B: Subscribe to a Plan
1. Click **"Upgrade Plan"**
2. Choose a plan:
   - **Build Plan**: $25/month (includes credits)
   - **Scale Plan**: Custom pricing for high volume
3. Set up billing
4. Confirm subscription

---

## 💰 Pricing Information (as of 2024)

### Claude Sonnet 4 (your current model)
- **Input**: ~$3 per million tokens
- **Output**: ~$15 per million tokens

### Example Costs
| Task | Approximate Cost |
|------|------------------|
| Single formula generation | ~$0.01 - $0.03 |
| 100 formula generations | ~$1 - $3 |
| Testing suite (10 runs) | ~$0.10 - $0.30 |
| Daily development | ~$2 - $10 |

**Your test** (3 formulas) would cost approximately: **$0.03 - $0.09**

---

## 🔍 Check Your Current Balance

### Via Console (Web UI)
1. Go to: https://console.anthropic.com/settings/plans
2. Look for **"Current Balance"** or **"Credits Remaining"**
3. You'll see something like: "$0.00" or "$5.00 remaining"

### Via API (Programmatic)
```python
# Unfortunately, Anthropic doesn't provide a direct API endpoint
# to check balance. You need to check via the console.
```

---

## ⚡ When Do You Need Credits?

### You NEED credits for:
- ✅ Making API calls to Claude models
- ✅ Formula generation with AnthropicProvider
- ✅ Any real-time AI interactions
- ✅ Production applications

### You DON'T need credits for:
- ❌ Using mock/test providers (like the mock test provided)
- ❌ Using DeFi calculation tools (uniswap_v2.py, il_calculator.py)
- ❌ Running local computations
- ❌ Testing code structure and imports

---

## 🚀 Recommended Approach

### For Development/Testing
```bash
# Start with mock tests (no credits needed)
python ./tests/unit/test_tools/test_anthropic_provider_mock.py

# Use DeFi tools independently
python -c "
from tools.domains.finance.defi.uniswap_v2 import UniswapV2Pool
pool = UniswapV2Pool(1000, 2000000)
print(pool.get_pool_info())
"

# When ready, add $5-$20 credits for real API testing
```

### For Production
1. **Start with Build Plan** ($25/month with included credits)
2. **Monitor usage** through console
3. **Set up billing alerts** to avoid surprises
4. **Scale up** as needed

---

## 🔐 Managing API Keys

### Best Practices
1. **Never commit API keys to Git**
   ```bash
   # Make sure .env is in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables**
   ```bash
   # In .env file
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```

3. **Rotate keys regularly** for security

4. **Use separate keys** for development vs production

### Create Additional Keys
1. Go to: https://console.anthropic.com/settings/keys
2. Click **"Create Key"**
3. Name it (e.g., "Development", "Production")
4. Copy and store securely
5. Update your `.env` file

---

## 🛠️ Troubleshooting

### "Credit balance too low" Error
**Solution**: Add credits through console (steps above)

### "Invalid API Key" Error
**Possible causes**:
- Key is incorrect or has typos
- Key was revoked or expired
- Key is not properly loaded from .env

**Solution**:
```bash
# Verify key in .env
cat .env | grep ANTHROPIC

# Test key format (should start with sk-ant-)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:15])"
```

### "Rate limit exceeded" Error
**Solution**:
- Wait a few minutes before retrying
- Upgrade to higher tier plan for increased limits
- Implement retry logic with exponential backoff

---

## 📊 Usage Tracking

### Monitor Your Usage
1. Go to: https://console.anthropic.com/settings/usage
2. View:
   - Daily/monthly token usage
   - Cost breakdown by model
   - Request counts
   - Error rates

### Set Up Alerts
1. In console, go to **Billing Settings**
2. Enable **"Usage Alerts"**
3. Set threshold (e.g., alert at 80% of budget)
4. Add email for notifications

---

## 🎓 Free Credits for Learning

### New Account Credits
- Anthropic sometimes offers **$5-$10 free credits** for new accounts
- Check during sign-up or promotional periods

### Educational Programs
- Check if you qualify for:
  - Student discounts
  - Academic research programs
  - Open-source project grants

---

## 📞 Support

### Need Help?
- **Documentation**: https://docs.anthropic.com
- **Support Email**: support@anthropic.com
- **Discord Community**: Check Anthropic's website for invite link
- **Status Page**: https://status.anthropic.com

---

## ✅ Checklist: Before Running Tests with Real API

- [ ] Account created at console.anthropic.com
- [ ] Credits added ($5-$20 recommended for testing)
- [ ] API key generated and saved
- [ ] API key added to `.env` file
- [ ] `.env` file in `.gitignore`
- [ ] Test with mock provider first (validates code)
- [ ] Usage alerts configured
- [ ] Ready to run real tests!

---

## 🔄 Summary

1. **Right now**: Use the mock test (no credits needed)
2. **When ready**: Add $5-$20 credits to your account
3. **Then**: Switch from MockAnthropicProvider to AnthropicProvider
4. **Monitor**: Watch usage and costs through console
5. **Scale**: Upgrade plan as your needs grow

**The mock test I provided works perfectly without any credits and validates your entire setup!** 🎉