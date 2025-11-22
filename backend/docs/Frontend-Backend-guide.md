# Frontend-Backend Integration Guide

## 📁 File Structure

```
frontend/
├── js/
│   ├── api-client.js           # ✅ Core API client (CREATED)
│   ├── main.js                 # ✅ HypatiaX integration (CREATED)
│   ├── dashboard.js            # ✅ DeFi dashboard (CREATED)
│   └── ner-demo.js             # ✅ NER demo (CREATED)
├── css/
│   ├── components.css          # ✅ Component styles (CREATED)
│   └── main.css                # ⚠️ Add base styles
├── index.html                  # ⚠️ Update with new scripts
├── dashboard.html              # ⚠️ Update with new scripts
└── ner-demo.html               # ⚠️ Update with new scripts
```

## 🔧 Step 1: Update HTML Files

### A. Update `index.html` (HypatiaX)

Add before closing `</body>`:

```html
<!-- Core API Client -->
<script src="js/api-client.js"></script>
<!-- HypatiaX Main -->
<script src="js/main.js"></script>
```

Add this HTML structure in the `<body>`:

```html
<div class="container">
    <!-- API Status -->
    <div id="api-status" class="api-status">Checking connection...</div>
    
    <!-- Demo Warning (shown in demo mode) -->
    <div id="demo-warning"></div>
    
    <!-- Main Form -->
    <div class="card">
        <h1>HypatiaX Formula Mapper</h1>
        <p>Convert natural language to Tableau formulas</p>
        
        <form id="formula-form">
            <div class="form-group">
                <label for="description-input">Describe what you want to calculate:</label>
                <input 
                    type="text" 
                    id="description-input" 
                    name="description" 
                    placeholder="e.g., Calculate the total of Sales"
                    required
                />
            </div>
            
            <div class="form-group">
                <label for="method-select">Method:</label>
                <select id="method-select" name="method">
                    <option value="vocab">Vocabulary-based</option>
                    <option value="semantic">Semantic Analysis</option>
                </select>
            </div>
            
            <!-- Quick Suggestion -->
            <div id="quick-suggestion"></div>
            
            <button type="submit" class="btn-primary">Generate Formula</button>
        </form>
        
        <!-- Example Queries -->
        <div class="examples">
            <h3>Try these examples:</h3>
            <button class="example-query-btn" data-query="Calculate the total of Sales">
                Sum of Sales
            </button>
            <button class="example-query-btn" data-query="Average of Profit">
                Average Profit
            </button>
            <button class="example-query-btn" data-query="Count of Orders">
                Count Orders
            </button>
        </div>
    </div>
    
    <!-- Results -->
    <div id="formula-result"></div>
    
    <!-- Test Button -->
    <button id="test-hypatiax-btn" class="btn-secondary">Run Tests</button>
    <div id="test-results"></div>
</div>
```

### B. Update `dashboard.html` (DeFi)

Add before closing `</body>`:

```html
<!-- Core API Client -->
<script src="js/api-client.js"></script>
<!-- Dashboard -->
<script src="js/dashboard.js"></script>
```

Add this HTML structure:

```html
<div class="container">
    <!-- API Status -->
    <div id="api-status" class="api-status">Checking connection...</div>
    
    <h1>DeFi Position Analyzer</h1>
    
    <!-- Quick IL Calculator -->
    <div class="card">
        <h2>Quick IL Calculator</h2>
        <form id="quick-il-form">
            <div class="form-row">
                <div class="form-group">
                    <label>Initial Price:</label>
                    <input type="number" name="initial_price" step="0.01" required />
                </div>
                <div class="form-group">
                    <label>Current Price:</label>
                    <input type="number" name="current_price" step="0.01" required />
                </div>
            </div>
            <div id="price-change-preview"></div>
            <button type="submit" class="btn-primary">Calculate IL</button>
        </form>
        <div id="quick-il-result"></div>
    </div>
    
    <!-- Full Position Analysis -->
    <div class="card">
        <h2>Complete Position Analysis</h2>
        <form id="position-analysis-form">
            <h3>Initial Position</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>Token A Amount:</label>
                    <input type="number" name="initial_token_a" step="0.01" required />
                </div>
                <div class="form-group">
                    <label>Token B Amount:</label>
                    <input type="number" name="initial_token_b" step="0.01" required />
                </div>
            </div>
            
            <h3>Prices</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>Initial Price:</label>
                    <input type="number" name="initial_price" step="0.01" required />
                </div>
                <div class="form-group">
                    <label>Current Price:</label>
                    <input type="number" name="current_price" step="0.01" required />
                </div>
            </div>
            
            <h3>Pool Information</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>Daily Volume (USD):</label>
                    <input type="number" name="daily_volume_usd" step="1" required />
                </div>
                <div class="form-group">
                    <label>Pool TVL (USD):</label>
                    <input type="number" name="pool_tvl_usd" step="1" required />
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Days Elapsed:</label>
                    <input type="number" name="days_elapsed" min="1" required />
                </div>
                <div class="form-group">
                    <label>Fee Rate (%):</label>
                    <input type="number" name="fee_rate" value="0.003" step="0.001" />
                </div>
            </div>
            
            <button type="submit" class="btn-primary">Analyze Position</button>
            <button type="button" class="btn-secondary" onclick="window.location.href='?example=true'">
                Load Example
            </button>
        </form>
        <div id="position-analysis-result"></div>
    </div>
</div>
```

### C. Update `ner-demo.html`

Add before closing `</body>`:

```html
<!-- Core API Client -->
<script src="js/api-client.js"></script>
<!-- NER Demo -->
<script src="js/ner-demo.js"></script>
<!-- MathJax for LaTeX rendering -->
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

Add this HTML structure:

```html
<div class="container">
    <!-- API Status -->
    <div id="api-status" class="api-status">Checking connection...</div>
    
    <h1>Formula Extraction & Analysis</h1>
    
    <!-- Examples -->
    <div class="examples">
        <h3>Try these examples:</h3>
        <button class="example-btn" data-example="defi">DeFi (IL Formula)</button>
        <button class="example-btn" data-example="finance">Finance (NPV)</button>
        <button class="example-btn" data-example="physics">Physics (E=mc²)</button>
        <button class="example-btn" data-example="calculus">Calculus (Derivative)</button>
    </div>
    
    <!-- Tabs -->
    <div class="tabs">
        <button class="tab-btn active" data-tab="extraction">Formula Extraction</button>
        <button class="tab-btn" data-tab="entities">Entity Recognition</button>
        <button class="tab-btn" data-tab="latex">LaTeX Conversion</button>
    </div>
    
    <!-- Extraction Tab -->
    <div id="extraction-tab" class="tab-content active">
        <div class="card">
            <form id="extract-formula-form">
                <div class="form-group">
                    <label>Enter text containing a formula:</label>
                    <textarea name="formula_text" rows="3" required 
                              placeholder="e.g., IL = 2*sqrt(r)/(r+1) - 1"></textarea>
                </div>
                <div class="form-group">
                    <label>Domain:</label>
                    <select name="domain">
                        <option value="general">General</option>
                        <option value="defi">DeFi</option>
                        <option value="finance">Finance</option>
                        <option value="physics">Physics</option>
                        <option value="mathematics">Mathematics</option>
                    </select>
                </div>
                <button type="submit" class="btn-primary">Extract Formula</button>
            </form>
            <div id="extraction-result"></div>
        </div>
    </div>
    
    <!-- Entity Recognition Tab -->
    <div id="entities-tab" class="tab-content">
        <div class="card">
            <form id="entity-recognition-form">
                <div class="form-group">
                    <label>Enter text to analyze:</label>
                    <textarea name="entity_text" rows="3" required></textarea>
                </div>
                <button type="submit" class="btn-primary">Recognize Entities</button>
            </form>
            <div id="entity-result"></div>
        </div>
    </div>
    
    <!-- LaTeX Tab -->
    <div id="latex-tab" class="tab-content">
        <div class="card">
            <form id="latex-conversion-form">
                <div class="form-group">
                    <label>Enter formula to convert:</label>
                    <textarea name="latex_formula" rows="2" required 
                              placeholder="e.g., sqrt(x^2 + y^2)"></textarea>
                </div>
                <button type="submit" class="btn-primary">Convert to LaTeX</button>
            </form>
            <div id="latex-result"></div>
        </div>
    </div>
    
    <!-- Copy Notification -->
    <div id="copy-notification"></div>
</div>
```

## 🎨 Step 2: Add CSS

Link the CSS files in all HTML `<head>` sections:

```html
<link rel="stylesheet" href="css/main.css">
<link rel="stylesheet" href="css/components.css">
```

Create `css/main.css` with base styles:

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f9fafb;
    color: #111827;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: #111827;
}

h2 {
    font-size: 1.75rem;
    margin: 1.5rem 0 1rem;
    color: #374151;
}

h3 {
    font-size: 1.25rem;
    margin: 1rem 0 0.5rem;
    color: #4b5563;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-family: inherit;
}

.form-group textarea {
    resize: vertical;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

@media (max-width: 768px) {
    .form-row {
        grid-template-columns: 1fr;
    }
}
```

## 🚀 Step 3: Start the Backend

```bash
cd backend
python app.py
```

The server should start on `http://localhost:5000`

## ✅ Step 4: Test the Integration

### Test 1: Health Check
Open browser console and run:
```javascript
api.healthCheck().then(console.log);
```

### Test 2: HypatiaX
Navigate to `index.html` and try:
- "Calculate the total of Sales"
- "Average of Profit"

### Test 3: DeFi Calculator
Navigate to `dashboard.html` and enter:
- Initial Price: 2000
- Current Price: 3000
- Click "Calculate IL"

### Test 4: NER Demo
Navigate to `ner-demo.html` and try:
- Click "DeFi (IL Formula)" example
- Click "Extract Formula"

## 🐛 Troubleshooting

### CORS Errors
If you see CORS errors, the backend already has CORS enabled:
```python
from flask_cors import CORS
CORS(app)
```

### Connection Refused
1. Ensure backend is running: `python app.py`
2. Check URL in `api-client.js` matches your backend
3. Verify port 5000 is not in use

### API Not Responding
1. Check browser console for errors
2. Verify API status badge shows "Connected"
3. Test endpoints with curl:
```bash
curl http://localhost:5000/api/health
```

## 📊 API Endpoints Reference

### HypatiaX
- `POST /api/hypatiax/map` - Map description to formula
- `GET /api/hypatiax/test` - Run test queries

### NER
- `POST /api/ner/extract-formula` - Extract formula from text
- `POST /api/ner/recognize-entities` - Recognize entities
- `POST /api/ner/convert-to-latex` - Convert to LaTeX

### DeFi
- `POST /api/defi/il-percentage` - Calculate IL percentage
- `POST /api/defi/analyze-position` - Complete position analysis

## 🎉 You're Done!

Your frontend is now fully integrated with the backend. All features should work:

✅ Real-time API health checking
✅ HypatiaX formula generation
✅ DeFi position analysis
✅ NER formula extraction
✅ Error handling and loading states
✅ Responsive design

## 📝 Next Steps

1. Customize styling in `css/main.css` and `css/components.css`
2. Add more example queries
3. Implement user authentication (optional)
4. Add data persistence
5. Deploy to production