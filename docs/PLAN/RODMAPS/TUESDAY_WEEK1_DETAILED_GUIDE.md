# TUESDAY WEEK 1: DETAILED HOUR-BY-HOUR GUIDE
## Market Validation - Protocol Outreach (3 Hours)

---

## **HOUR 1: RESEARCH CURRENT RISK TOOLS**

### **What You're Doing**
Investigating what risk management tools Aave, Uniswap, and Compound currently use, and identifying their pain points by reading their community discussions.

### **Why This Matters**
You need to understand:
1. What tools they're already using (so you don't duplicate)
2. What they're complaining about (your opportunity)
3. How they talk about risk (so you speak their language)
4. Who makes decisions about tools (who to contact)

---

### **Step-by-Step: Aave Research (20 minutes)**

#### **A. Join Aave Discord** (5 min)
1. Go to: https://aave.com/ → Click "Community" → "Discord"
2. Join the server
3. Navigate to these channels:
   - `#governance` - where risk parameters are discussed
   - `#risk-management` - if it exists
   - `#general` - for recent discussions
   - `#developer` - to see technical pain points

#### **B. Search for Pain Points** (10 min)
In Discord search bar (Ctrl+K or Cmd+K), search for these terms:
- "liquidation"
- "health factor"
- "risk monitoring"
- "collateral ratio"
- "oracle"
- "bad debt"

**What to look for:**
- Complaints like "I wish we had..."
- Questions like "How do we track..."
- Incidents like "The liquidation cascade..."
- Tool mentions like "We use Gauntlet for..."

#### **C. Document Findings** (5 min)
Open a Google Doc or Notion page titled "Protocol Research Notes"

Create this structure:
```
## AAVE

### Current Tools They Use:
- [Tool name]: [What it does]
- Example: Gauntlet: Risk parameter recommendations

### Pain Points Mentioned:
1. [Specific complaint or need]
   - Source: [Discord channel, date]
   - Quote: "[exact words]"

### Key People:
- [Name]: [Role] - [Twitter handle if found]

### Technical Details:
- Total Value Locked (TVL): [Look up on DeFiLlama]
- Main risk concerns: [List 2-3]
```

**Example entry:**
```
### Pain Points Mentioned:
1. Manual monitoring of health factors is time-consuming
   - Source: #governance, Jan 15
   - Quote: "Wish we had real-time alerts when health factors drop below 1.2"

2. Gauntlet reports are monthly, need more frequent updates
   - Source: #risk-management, Jan 20
   - Quote: "By the time we get the report, market conditions have changed"
```

---

### **Step-by-Step: Uniswap Research** (20 minutes)

#### **A. Join Uniswap Discord** (5 min)
1. Go to: https://uniswap.org/ → "Community" → "Discord"
2. Navigate to channels:
   - `#governance`
   - `#v4-hooks` (new feature, likely pain points here)
   - `#liquidity-providers`
   - `#general`

#### **B. Search for Pain Points** (10 min)
Search terms:
- "impermanent loss"
- "IL calculator"
- "LP returns"
- "hook risk"
- "position management"
- "v4 migration"

**Uniswap-specific things to note:**
- V4 is new, lots of uncertainty about hooks
- LPs complain about IL calculations
- Position optimization is a common topic

#### **C. Document Findings** (5 min)
Add to your Google Doc:
```
## UNISWAP

### Current Tools They Use:
- [What you find]

### Pain Points Mentioned:
1. [Specific need]
   - Source: [Channel]
   - Quote: "[words]"

### V4-Specific Concerns:
- [New hook risks]
- [Migration challenges]

### Key People:
- [Names and roles]
```

---

### **Step-by-Step: Compound Research** (20 minutes)

#### **A. Join Compound Discord/Forums** (5 min)
1. Go to: https://compound.finance/ → "Community"
2. Join Discord: https://discord.com/invite/compound
3. Also check: https://www.comp.xyz/ (Compound governance forum)

Key channels:
- `#governance`
- `#general`
- `#developer`

#### **B. Search for Pain Points** (10 min)
Search terms:
- "supply rate"
- "borrow rate"
- "liquidation"
- "oracle risk"
- "collateral"
- "utilization"

**Compound-specific focuses:**
- Interest rate model adjustments
- Collateral risk for new assets
- Governance proposal analytics

#### **C. Document Findings** (5 min)
Add to Google Doc using same structure as above.

---

### **HOUR 1 OUTPUT**
By end of Hour 1, you should have:
- ✅ Google Doc with 3 protocol sections
- ✅ 2-3 pain points per protocol
- ✅ 1-2 current tools they use per protocol
- ✅ 2-3 key people names
- ✅ Understanding of their biggest risk concerns

**If you find nothing in Discord:**
- Check their governance forums (comp.xyz, governance.aave.com)
- Read recent governance proposals (search "risk parameter")
- Check Twitter for complaints by protocol users
- Look at Dune Analytics dashboards they share

---

## **HOUR 2: CRAFT PERSONALIZED OUTREACH MESSAGES**

### **What You're Doing**
Writing and sending customized messages to 3 protocols, and joining Risk DAO.

### **Why This Matters**
Generic messages get ignored. You need to show you understand THEIR specific pain point.

---

### **Step 1: Find the Right People (15 min)**

#### **For Each Protocol, Find:**

**Aave - Who to Contact:**
1. **Twitter Search:**
   - Go to Twitter
   - Search: `Aave risk management` or `@AaveAave contributors`
   - Look for:
     - Risk team members
     - Governance contributors
     - Protocol economists
   
2. **Likely Contacts:**
   - Check Aave's governance forum for active participants
   - Look for "Risk Team" or "Risk Contributors" in Discord roles
   - Example targets:
     - @MarcZeller (Governance)
     - @llama (Risk/Treasury contributors)
     - Anyone with "Risk" in their Discord role

3. **Where to Message:**
   - **Best**: Twitter DM (most likely to see it)
   - **Good**: Discord DM (if they're active there)
   - **Backup**: Tag in governance forum

**Uniswap - Who to Contact:**
1. **Twitter Search:**
   - Search: `Uniswap governance` or `Uniswap v4`
   - Look for:
     - Uniswap Labs team
     - Uniswap Foundation
     - V4 hook developers
   
2. **Likely Contacts:**
   - Governance forum active members
   - @Uniswap Foundation team
   - Hook developers (they need risk tools)

3. **Where to Message:**
   - Twitter DM
   - Discord (especially in #v4-hooks channel)

**Compound - Who to Contact:**
1. **Twitter Search:**
   - Search: `Compound governance` or `@compoundfinance`
   
2. **Likely Contacts:**
   - Governance forum participants
   - OpenZeppelin (they do risk assessments for Compound)
   - Gauntlet (consulting partner)

3. **Where to Message:**
   - comp.xyz forum (public post)
   - Twitter DM
   - Discord

---

### **Step 2: Write Personalized Messages (30 min)**

#### **Message Template Structure:**
1. Hook (mention specific pain point you found)
2. What you're building (one sentence)
3. Specific benefit for THEIR protocol
4. Soft ask (not pushy)

---

#### **EXAMPLE: Aave Message**

**If you found: "Manual health factor monitoring is tedious"**

```
Subject: Automated Health Factor Monitoring for Aave

Hi [Name],

I noticed in the Aave governance Discord that manual health factor monitoring 
is time-consuming, and Gauntlet reports come monthly but markets move daily.

I'm building an AI system that automatically discovers and validates risk 
formulas for DeFi protocols using symbolic regression. It can generate 
real-time health factor predictions and liquidation risk alerts.

For Aave specifically, it could:
- Monitor health factors across all positions continuously
- Alert when aggregate risk crosses thresholds
- Predict liquidation cascades before they happen

Would you be interested in seeing a 15-minute demo of the system analyzing 
Aave's recent liquidation events?

No pressure - just thought it might be useful for the risk team.

Best,
[Your Name]

P.S. I've been following Aave's governance and really impressed by your 
approach to risk management. Happy to share my research even if the tool 
isn't a fit.
```

**Why this works:**
- ✅ Shows you did research (mentions specific pain point)
- ✅ Specific to Aave (not generic)
- ✅ Clear value proposition
- ✅ Low-pressure ask
- ✅ Genuine compliment (builds rapport)

---

#### **EXAMPLE: Uniswap Message**

**If you found: "V4 hook risk is uncertain"**

```
Subject: Risk Analysis for Uniswap V4 Hooks

Hi [Name],

Saw the discussion in #v4-hooks about uncertainty around hook security and 
risk implications for liquidity providers.

I'm building an AI-powered risk analytics system that uses symbolic regression 
to discover formulas for DeFi risk metrics. 

For Uniswap V4, it could:
- Analyze IL patterns across different hook configurations
- Score hook risk based on historical behavior
- Help LPs optimize position management with hooks

I ran some preliminary analysis on V3 IL patterns and found some interesting 
results. Would you be interested in a quick 15-min demo showing how it could 
work for V4?

Happy to share my findings either way.

Best,
[Your Name]
```

---

#### **EXAMPLE: Compound Message**

**If you found: "Need better collateral risk assessment"**

```
Subject: Collateral Risk Analytics for Compound

Hi [Name],

Following Compound governance proposals, I noticed several discussions about 
how to assess collateral risk for new asset listings - especially with 
Oracle dependencies.

I'm building an AI system that automatically discovers and validates risk 
formulas using symbolic regression + LLM interpretation.

For Compound, it could:
- Analyze collateral ratio safety margins
- Predict supply/borrow rate impacts from new listings
- Model liquidation risk under various market scenarios

Would you be interested in seeing a 15-minute demo applied to Compound's 
recent governance decisions?

Best,
[Your Name]
```

---

### **Step 3: Send Messages (10 min)**

#### **Twitter DM:**
1. Go to recipient's Twitter profile
2. Click "Message"
3. Paste your personalized message
4. Send

#### **Discord DM:**
1. Find person in Discord member list
2. Right-click → "Message"
3. Paste personalized message
4. Send

#### **If can't DM:**
- Post in appropriate channel (e.g., #governance) tagging them
- Or reply to one of their messages with your pitch

---

### **Step 4: Join Risk DAO (5 min)**

**What is Risk DAO:**
Community-driven risk assessment DAO for DeFi protocols.

**How to Join:**
1. Go to: https://www.riskdao.org/
2. Click "Join Discord" or search "Risk DAO Discord" on Google
3. Join Discord server
4. Introduce yourself in #introductions:
```
Hey everyone! I'm building an AI-powered risk analytics tool for DeFi 
protocols using symbolic regression. Excited to learn from this community 
and contribute where I can. Currently focused on liquidation risk and IL 
analysis. Happy to connect!
```

5. Navigate to relevant channels:
   - `#general`
   - `#risk-analysis`
   - `#research`

**Why Join Risk DAO:**
- Learn how other risk analysts think
- See what tools they use/need
- Potential customers (protocols hire Risk DAO members)
- Credibility (being active here helps)

---

### **HOUR 2 OUTPUT**
By end of Hour 2, you should have:
- ✅ 3 personalized messages sent (Aave, Uniswap, Compound)
- ✅ Joined Risk DAO Discord
- ✅ Introduction posted in Risk DAO

---

## **HOUR 3: SET UP TRACKING SPREADSHEET**

### **What You're Doing**
Creating a systematic way to track all 10 protocols, your outreach, their responses, and pilot interest.

### **Why This Matters**
- You'll forget details without tracking
- Need to follow up systematically
- Measure progress toward "3 pilots" goal
- Document learnings for decision in Week 4

---

### **Step 1: Create Google Sheet (5 min)**

1. Go to: https://sheets.google.com
2. Create new spreadsheet
3. Name it: "DeFi Risk Analytics - Protocol Outreach Tracker"

---

### **Step 2: Set Up Columns (10 min)**

Create these column headers in Row 1:

| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| Protocol | TVL | Status | Contact Name | Contact Method | Date Contacted | Response Date | Top Pain Point | Current Tools | Pilot Interest | Notes |

**Column Descriptions:**

- **A - Protocol**: Name (Aave, Uniswap, etc.)
- **B - TVL**: Total Value Locked (for prioritization)
- **C - Status**: Not Contacted / Contacted / Responded / Demo Scheduled / Pilot Committed
- **D - Contact Name**: Person you messaged
- **E - Contact Method**: Twitter DM / Discord / Email / Forum
- **F - Date Contacted**: When you sent first message
- **G - Response Date**: When they replied (if they did)
- **H - Top Pain Point**: Their biggest risk management pain point
- **I - Current Tools**: What they use now (Gauntlet, Dune, internal, etc.)
- **J - Pilot Interest**: None / Low / Medium / High / Committed
- **K - Notes**: Free text for anything important

---

### **Step 3: Add 10 Target Protocols (20 min)**

Fill in these rows with the protocols from your outreach plan:

#### **Row 2 - Aave**
```
Protocol: Aave
TVL: $10B+ (check DeFiLlama for current)
Status: Contacted
Contact Name: [whoever you messaged]
Contact Method: Twitter DM
Date Contacted: [today's date]
Response Date: [leave blank]
Top Pain Point: [from your Hour 1 research]
Current Tools: Gauntlet, Chaos Labs
Pilot Interest: [leave blank until they respond]
Notes: Largest lending protocol, focus on liquidation risk
```

#### **Row 3 - Uniswap**
```
Protocol: Uniswap
TVL: $5B+
Status: Contacted
Contact Name: [whoever you messaged]
Contact Method: Discord
Date Contacted: [today's date]
Response Date: [leave blank]
Top Pain Point: V4 hook risk uncertainty, IL calculations
Current Tools: Internal analytics, various IL calculators
Pilot Interest: [leave blank]
Notes: V4 launching, hooks are new risk vector
```

#### **Row 4 - Compound**
```
Protocol: Compound
TVL: $3B+
Status: Contacted
Contact Name: [whoever you messaged]
Contact Method: comp.xyz forum
Date Contacted: [today's date]
Response Date: [leave blank]
Top Pain Point: Collateral risk for new assets
Current Tools: OpenZeppelin, Gauntlet
Pilot Interest: [leave blank]
Notes: Strong governance, risk-focused
```

#### **Rows 5-11 - Remaining Protocols**
Add these (you'll contact them Thu/Fri):
- MakerDAO / Sky
- Curve Finance
- Morpho
- Lido Finance
- GMX
- Euler Finance
- Balancer

For these, fill in:
- Protocol name
- TVL (look up on https://defillama.com)
- Status: "Not Contacted"
- Leave other fields blank for now

---

### **Step 4: Add Conditional Formatting (15 min)**

Make the spreadsheet easier to scan visually.

#### **A. Status Column Color Coding:**
1. Select column C (Status)
2. Format → Conditional formatting
3. Set up these rules:

**Rule 1:**
- Format cells if: Text contains "Not Contacted"
- Background color: Light gray (#f3f3f3)

**Rule 2:**
- Format cells if: Text contains "Contacted"
- Background color: Light yellow (#fff4cc)

**Rule 3:**
- Format cells if: Text contains "Responded"
- Background color: Light blue (#cfe2ff)

**Rule 4:**
- Format cells if: Text contains "Demo Scheduled"
- Background color: Light purple (#e7d6ff)

**Rule 5:**
- Format cells if: Text contains "Pilot Committed"
- Background color: Light green (#d4edda)

#### **B. Pilot Interest Color Coding:**
1. Select column J (Pilot Interest)
2. Format → Conditional formatting

**Rule 1:**
- Format cells if: Text contains "None" or "Low"
- Background color: Light red (#f8d7da)

**Rule 2:**
- Format cells if: Text contains "Medium"
- Background color: Light yellow (#fff4cc)

**Rule 3:**
- Format cells if: Text contains "High" or "Committed"
- Background color: Light green (#d4edda)

---

### **Step 5: Add Summary Section (10 min)**

In Row 13 (below your 10 protocols), create summary metrics:

```
[Leave Row 12 blank for spacing]

Row 13:
A: "SUMMARY METRICS"
[Bold this row]

Row 14:
A: "Total Protocols"
B: =COUNTA(A2:A11)

Row 15:
A: "Contacted"
B: =COUNTIF(C2:C11,"Contacted") + COUNTIF(C2:C11,"Responded") + COUNTIF(C2:C11,"Demo Scheduled") + COUNTIF(C2:C11,"Pilot Committed")

Row 16:
A: "Responded"
B: =COUNTIF(C2:C11,"Responded") + COUNTIF(C2:C11,"Demo Scheduled") + COUNTIF(C2:C11,"Pilot Committed")

Row 17:
A: "Demos Scheduled"
B: =COUNTIF(C2:C11,"Demo Scheduled")

Row 18:
A: "Pilots Committed"
B: =COUNTIF(C2:C11,"Pilot Committed")

Row 19:
A: "Response Rate"
B: =B16/B15
[Format as percentage]

Row 20:
A: "Conversion Rate (Responded → Pilot)"
B: =B18/B16
[Format as percentage]
```

This gives you live tracking of your progress!

---

### **Step 6: Add Follow-Up Tracker (Optional but Recommended)**

Create a second sheet in the same Google Sheets file:

**Sheet 2 Name: "Follow-Up Schedule"**

Columns:
| Protocol | Contact | Last Contact Date | Next Follow-Up Date | Follow-Up Type | Status |

This helps you remember to follow up without being annoying.

**Follow-up rules:**
- Wait 3 days after initial contact
- If no response, follow up once
- Wait 5 days after follow-up
- If still no response, mark as "Low interest" and move on

---

### **HOUR 3 OUTPUT**
By end of Hour 3, you should have:
- ✅ Google Sheet with 10 protocols
- ✅ 3 protocols marked "Contacted"
- ✅ Color-coded status tracking
- ✅ Summary metrics that auto-update
- ✅ Research notes from Hour 1 linked or pasted in Notes column

---

## **END OF TUESDAY - CHECKLIST**

Before you finish, confirm you have:

**Hour 1 Deliverables:**
- [ ] Google Doc with research on Aave, Uniswap, Compound
- [ ] 2-3 pain points documented per protocol
- [ ] 1-2 current tools they use per protocol
- [ ] 2-3 key people identified per protocol

**Hour 2 Deliverables:**
- [ ] Sent personalized message to Aave contact
- [ ] Sent personalized message to Uniswap contact
- [ ] Sent personalized message to Compound contact
- [ ] Joined Risk DAO Discord
- [ ] Posted introduction in Risk DAO

**Hour 3 Deliverables:**
- [ ] Google Sheet "Protocol Outreach Tracker" created
- [ ] 10 protocols added to sheet
- [ ] 3 protocols marked as "Contacted" with details
- [ ] Conditional formatting applied
- [ ] Summary metrics working

---

## **COMMON PROBLEMS & SOLUTIONS**

### **Problem: Can't find anyone to contact at a protocol**
**Solution:**
- Search "[Protocol name] team" on Twitter
- Check their governance forum for active contributors
- Look at recent governance proposals for authors
- Ask in their Discord: "Who handles risk management decisions here?"

### **Problem: Discord DMs are closed**
**Solution:**
- Post in appropriate channel (tag them if possible)
- Use Twitter DM instead
- Comment on their governance forum post

### **Problem: Not finding pain points in Discord**
**Solution:**
- Check governance forums instead
- Read recent proposals (always mention risk)
- Look at Dune dashboards they share
- Search Twitter for "[Protocol] risk" or "[Protocol] liquidation"

### **Problem: No response to messages**
**Solution:**
- Normal! Expect 30-50% response rate
- Don't take it personally
- Follow up once after 3 days
- Move on if still no response
- Focus on the ones who do respond

### **Problem: Ran out of time**
**Solution:**
- Finish Hour 1 research first (most important)
- Send at least 1 message (better than none)
- Set up basic spreadsheet (you can enhance later)
- Continue on Thursday

---

## **PREPARATION FOR THURSDAY (WEEK 1, HOUR 4-6)**

Before Thursday, do these quick tasks:

**5-Minute Prep:**
1. Check if any of your 3 contacts responded
2. If yes, reply immediately and schedule demo
3. If no, don't worry - you'll follow up Thursday
4. Prepare messages for next 3 protocols: MakerDAO, Curve, Morpho

**What to Bring Thursday:**
- Your Google Doc with research notes
- Your tracking spreadsheet
- List of next 3 protocols to contact

---

## **MINDSET TIPS**

**You might feel:**
- Nervous about reaching out → Normal! These are just people
- Unsure if your message is good enough → Send it anyway, you can improve next time
- Worried no one will respond → You only need 3 pilots, not all 10

**Remember:**
- You're offering value (free risk analysis)
- Worst case: they ignore you (not the end of world)
- Best case: you find a pilot customer
- Most likely: you learn what the market needs

**Action beats perfection.**

Send the messages. Set up the sheet. Move forward.

See you Thursday for Hours 4-6! 🚀
