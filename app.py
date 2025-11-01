from flask import Flask, render_template, request, jsonify, session
import os
from pathlib import Path
import secrets
from llama_cpp import Llama
import requests
import json
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
MODEL_PATH = "model/model.gguf"  # Path to your GGUF model
DATA_FOLDER = "data"
API_KEY = "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"
API_MODEL = "openai/gpt-4o-mini"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize the model (will be loaded on first use)
llm = None

def load_model():
    """Load the GGUF model."""
    global llm
    if llm is None:
        model_file = Path(MODEL_PATH)
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please add your model.gguf file to the 'model' folder.")
        
        print(f"Loading model from {MODEL_PATH}...")
        llm = Llama(
            model_path=str(model_file),
            n_ctx=4096,  # Context window
            n_threads=4,  # Number of CPU threads to use
            n_gpu_layers=0,  # Set to -1 to use GPU if available
        )
        print("Model loaded successfully!")
    return llm

def read_documents_from_folder(folder_path):
    """Read all text files from the data folder and return their contents."""
    documents = []
    folder = Path(folder_path)
    
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        return documents
    
    # Support common file formats
    supported_extensions = ['.txt', '.md', '.json', '.csv']
    
    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append({
                        'filename': file_path.name,
                        'content': content
                    })
            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")
    
    return documents

def create_context_from_documents(documents):
    """Create a context string from all documents (with size limit)."""
    if not documents:
        return ""
    
    context = "Here is the information from the knowledge base:\n\n"
    max_context_length = 2000  # Limit context to avoid token overflow
    
    for doc in documents:
        doc_text = f"--- Document: {doc['filename']} ---\n{doc['content']}\n\n"
        if len(context) + len(doc_text) < max_context_length:
            context += doc_text
        else:
            # Truncate if too long
            remaining = max_context_length - len(context)
            if remaining > 100:
                context += doc_text[:remaining] + "...\n\n"
            break
    
    return context

def check_investment_query(user_message):
    """Check if the message is asking for investment advice."""
    investment_keywords = [
        'invest', 'investment', 'stock', 'stocks', 'ipo', 'share', 'shares',
        'buy', 'sell', 'trading', 'trade', 'portfolio', 'equity', 'equities',
        'mutual fund', 'should i buy', 'should i invest', 'good investment',
        'worth investing', 'market', 'bullish', 'bearish', 'nifty', 'sensex',
        'debt fund', 'bond', 'bonds', 'sip', 'lumpsum', 'diversify', 'asset allocation'
    ]
    
    message_lower = user_message.lower()
    return any(keyword in message_lower for keyword in investment_keywords)

def check_portfolio_query(user_message):
    """Check if the user wants a portfolio recommendation."""
    portfolio_keywords = [
        'portfolio', 'recommend investment', 'suggest investment', 'investment plan',
        'diversified portfolio', 'asset allocation', 'where to invest',
        'how should i invest', 'investment recommendation', 'build portfolio',
        'create portfolio', 'diversify', 'allocation', 'monthly investment'
    ]
    
    message_lower = user_message.lower()
    return any(keyword in message_lower for keyword in portfolio_keywords)

def extract_portfolio_parameters(user_message):
    """Extract investment parameters from user message."""
    import re
    
    params = {
        'capital': None,
        'monthly': None,
        'risk': 'medium',  # default
        'preferences': []
    }
    
    # Extract capital amount
    capital_patterns = [
        r'(?:capital|amount|invest|have)\s*(?:of|is)?\s*₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|lakhs|lacs|L)',
        r'(?:capital|amount|invest|have)\s*(?:of|is)?\s*₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr|crores)',
        r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|lac|lakhs|lacs|L|crore|cr|crores)?'
    ]
    
    for pattern in capital_patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            amount = float(amount_str)
            if 'lakh' in user_message.lower() or 'lac' in user_message.lower():
                params['capital'] = amount * 100000
            elif 'crore' in user_message.lower() or 'cr' in user_message.lower():
                params['capital'] = amount * 10000000
            else:
                params['capital'] = amount
            break
    
    # Extract monthly investment
    monthly_patterns = [
        r'(?:monthly|per month|every month)\s*(?:investment|invest|sip)?\s*(?:of)?\s*₹?\s*(\d+(?:,\d+)*)',
        r'(?:sip|monthly)\s*₹?\s*(\d+(?:,\d+)*)'
    ]
    
    for pattern in monthly_patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            params['monthly'] = float(match.group(1).replace(',', ''))
            break
    
    # Extract risk appetite
    if 'low risk' in user_message.lower() or 'conservative' in user_message.lower() or 'safe' in user_message.lower():
        params['risk'] = 'low'
    elif 'high risk' in user_message.lower() or 'aggressive' in user_message.lower():
        params['risk'] = 'high'
    elif 'medium risk' in user_message.lower() or 'moderate' in user_message.lower():
        params['risk'] = 'medium'
    
    # Extract preferences
    if 'mutual fund' in user_message.lower() or 'mf' in user_message.lower():
        params['preferences'].append('mutual_funds')
    if 'stock' in user_message.lower() or 'equity' in user_message.lower() or 'share' in user_message.lower():
        params['preferences'].append('stocks')
    if 'debt' in user_message.lower() or 'bond' in user_message.lower() or 'fixed' in user_message.lower():
        params['preferences'].append('debt')
    if 'gold' in user_message.lower():
        params['preferences'].append('gold')
    
    # If no preferences mentioned, include all
    if not params['preferences']:
        params['preferences'] = ['mutual_funds', 'stocks', 'debt', 'gold']
    
    return params

def generate_portfolio_recommendation(user_message, params):
    """Generate personalized portfolio recommendation using AI."""
    try:
        # If no capital specified, ask for it
        if not params['capital']:
            return """📊 **Portfolio Recommendation Service**

I'd be happy to create a personalized investment portfolio for you! To provide the best recommendations, I need some information:

**Please provide:**
1. **Investment Amount**: How much capital do you have? (e.g., "5 lakhs", "10 lakhs", "2 crores")
2. **Monthly Investment** (optional): Can you invest monthly via SIP? (e.g., "20,000 per month")
3. **Risk Appetite**: Low/Medium/High risk tolerance
4. **Preferences** (optional): Mutual funds, stocks, debt funds, bonds, gold

**Example:**
"I have 10 lakhs capital and can invest 25,000 monthly. Medium risk. I prefer mutual funds and stocks."

Once you provide these details, I'll create a comprehensive portfolio with:
✓ Specific mutual fund recommendations
✓ Stock picks from NSE/BSE
✓ Debt instruments and banks
✓ Asset allocation breakdown
✓ Expected returns
✓ Where to invest (platforms)

What are your investment details?"""

        portfolio_prompt = f"""You are an expert Indian financial advisor specializing in portfolio creation. Generate a detailed, personalized investment portfolio recommendation.

USER QUERY: {user_message}

INVESTMENT PARAMETERS:
- Capital Amount: ₹{params['capital']:,.0f} ({params['capital']/100000:.1f} Lakhs)
- Monthly SIP: ₹{params['monthly']:,.0f} per month (if specified)
- Risk Appetite: {params['risk'].upper()}
- Preferred Instruments: {', '.join(params['preferences']) if params['preferences'] else 'Open to all'}

CRITICAL INSTRUCTIONS:
1. Use your latest knowledge of Indian mutual funds, stocks, and market data
2. Provide actual fund names and stock symbols that exist
3. Use realistic current market data from your training
4. DO NOT mention that data is hypothetical or for demonstration
5. Present all information as if it's current and actionable
6. If you don't have exact current prices, use reasonable market ranges
7. Never write disclaimers about "hypothetical data" or "not having real-time data"
8. Present recommendations confidently using your knowledge base

TASK: Create a comprehensive investment portfolio with the following structure:

## 📊 RECOMMENDED PORTFOLIO ALLOCATION

**Total Investment:** ₹{params['capital']:,.0f}
**Risk Profile:** {params['risk'].upper()}

### Asset Allocation Breakdown:
Based on {params['risk']} risk, provide realistic percentages:
- **Equity (Direct Stocks)**: X% (₹XX,XXX)
- **Equity Mutual Funds**: X% (₹XX,XXX)
- **Debt Funds/Bonds**: X% (₹XX,XXX)
- **Gold/Gold ETF**: X% (₹XX,XXX)
- **Emergency Fund/Liquid**: X% (₹XX,XXX)

### 🎯 DETAILED INVESTMENT RECOMMENDATIONS:

#### 1️⃣ EQUITY MUTUAL FUNDS (Provide 5-7 specific funds)
For each fund provide:
- **Fund Name**: [Actual Indian MF name - use real funds like HDFC Top 100, Axis Bluechip, etc.]
- **Category**: Large Cap/Mid Cap/Small Cap/Flexi Cap
- **Recommended Amount**: ₹XX,XXX
- **Expected Returns**: X-X% p.a. (based on historical performance)
- **Why this fund**: Brief reason based on track record
- **SIP Suggestion**: ₹X,XXX/month (if monthly investment specified)

Use actual top-performing funds: HDFC Top 100, Axis Bluechip, Parag Parikh Flexi Cap, Mirae Asset Large Cap, Kotak Emerging Equity, SBI Small Cap, Motilal Oswal Midcap, etc.

#### 2️⃣ DIRECT STOCKS - NSE/BSE (Provide 8-10 stocks)
For each stock provide:
- **Stock Name** (NSE Symbol) - use real symbols
- **Sector**: IT/Banking/FMCG/Pharma/Auto/Infrastructure
- **Recommended Investment**: ₹XX,XXX
- **Approximate Price Range**: ₹XXX-XXX
- **Rationale**: Why this stock (fundamentals, growth potential)

Include diversified blue-chip and growth stocks: TCS, Infosys, HDFC Bank, ICICI Bank, Reliance Industries, ITC, HUL, Asian Paints, Dr. Reddy's, Maruti Suzuki, Bajaj Finance, etc.

#### 3️⃣ DEBT INSTRUMENTS (Provide 3-5 options)
- **Debt Mutual Funds**: Names (HDFC Corporate Bond Fund, ICICI Prudential Gilt Fund, Aditya Birla Sun Life Corporate Bond Fund, etc.)
- **Fixed Deposits**: Banks (SBI, HDFC Bank, ICICI Bank) with suggested tenure
- **Government Securities**: RBI Bonds, Sovereign Gold Bonds
- **Amount per instrument**: ₹XX,XXX
- **Expected Returns**: X-X% p.a.

#### 4️⃣ GOLD INVESTMENT
- **Gold ETFs**: HDFC Gold ETF, SBI Gold ETF, Nippon India Gold ETF
- **Sovereign Gold Bonds**: Latest available series
- **Amount**: ₹XX,XXX
- **Expected Returns**: X% p.a.

### 📈 PROJECTED RETURNS (5-Year Horizon)

Calculate based on historical returns and market trends:
- **Conservative Estimate**: X% CAGR = ₹XX,XXX final corpus
- **Realistic Estimate**: X% CAGR = ₹XX,XXX final corpus
- **Optimistic Estimate**: X% CAGR = ₹XX,XXX final corpus"""

        if params.get('monthly'):
            portfolio_prompt += f"""

### 💰 MONTHLY SIP PLAN

Distribute ₹{params['monthly']:,.0f}/month across:
- Equity MF 1: ₹X,XXX
- Equity MF 2: ₹X,XXX
- Balanced/Hybrid Fund: ₹X,XXX
- Debt Fund: ₹X,XXX"""

        portfolio_prompt += """

### ⚠️ RISK CONSIDERATIONS
List 3-5 specific risks for this portfolio

### 📋 ACTION PLAN
1. **Immediate Steps**: What to do first
2. **Account Setup**: Demat, trading account, MF KYC
3. **Platforms**: Zerodha, Groww, Paytm Money, etc.
4. **Monitoring**: How often to review
5. **Rebalancing**: When to rebalance

### 🔍 WHERE TO INVEST
- **Mutual Funds**: Groww, Paytm Money, Kuvera
- **Stocks**: Zerodha, Upstox, Angel One
- **Bonds/FD**: Bank websites, RBI Retail Direct
- **Gold**: Any of above platforms

IMPORTANT: 
- Be SPECIFIC with actual fund/stock names from Indian markets
- Use realistic market-based allocations for {params['risk']} risk profile
- Provide actionable recommendations based on your knowledge
- Do NOT add disclaimers about hypothetical or demonstration data
- Present everything as professional recommendations"""

        response = requests.post(
            url=API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": API_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert Indian financial advisor with deep knowledge of Indian mutual funds, NSE/BSE stocks, and investment products. You provide detailed, specific portfolio recommendations using your knowledge of actual Indian investment products. Never mention that you lack real-time data or that recommendations are hypothetical. Present all advice confidently based on your training data knowledge of Indian markets."
                    },
                    {
                        "role": "user",
                        "content": portfolio_prompt
                    }
                ],
                "temperature": 0.8,
                "max_tokens": 3000
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            portfolio = result['choices'][0]['message']['content']
            
            # Add disclaimer
            portfolio += """\n\n---

## ⚠️ IMPORTANT DISCLAIMERS

**This is an educational portfolio recommendation, NOT financial advice.**

✓ **Past performance ≠ future results** - Markets are subject to risk
✓ **Consult SEBI-registered advisor** before investing
✓ **Verify all details** on AMC/company websites  
✓ **Check latest NAV/prices** before investing
✓ **Understand tax implications** - LTCG, STCG
✓ **Maintain emergency fund** (6 months expenses)
✓ **Read all scheme documents** carefully

## 📚 VERIFY AT:
- **AMFI India**: www.amfiindia.com
- **NSE/BSE**: www.nseindia.com, www.bseindia.com
- **SEBI**: www.sebi.gov.in

**Have questions? Ask me about any specific recommendation!**"""
            
            return portfolio
        else:
            error_msg = f"API returned status {response.status_code}"
            print(f"Portfolio API Error: {error_msg} - {response.text}")
            return f"""I encountered an API error while generating your portfolio: {error_msg}

Please try asking again with this format:

"Create a portfolio for ₹[amount] lakhs with [low/medium/high] risk. I prefer [mutual funds/stocks/debt funds/gold]"

Example: "Create a portfolio for 10 lakhs with medium risk. I prefer mutual funds and stocks"

Or ask me general investment questions like:
- "What are the best mutual funds for 2024?"
- "How to start investing in stocks?"
- "Explain debt funds vs equity funds"
"""
            
    except Exception as e:
        error_details = str(e)
        print(f"Portfolio generation error: {error_details}")
        return f"""I encountered an error: {error_details}

Let me help you differently. Please provide:

**Investment Details:**
1. Capital amount (e.g., "5 lakhs", "10 lakhs")
2. Monthly SIP if any (e.g., "20,000/month")
3. Risk level (low/medium/high)
4. Preferences (mutual funds, stocks, debt, gold)

**Example query:**
"I want to invest 10 lakhs with medium risk in mutual funds and stocks. I can also do SIP of 25,000 monthly."

Or ask general questions like:
- Best mutual funds in India
- How to choose stocks
- Investment strategies"""

def extract_company_name(user_message):
    """Extract company/stock name from the message."""
    # Common patterns for company mentions
    patterns = [
        r'(?:invest in|buy|sell|about|regarding)\s+([A-Z][A-Za-z\s&]+?)(?:\s+(?:stock|shares|ipo|company))',
        r'([A-Z][A-Za-z\s&]+?)\s+(?:stock|shares|ipo|company)',
        r'(?:stock|shares|ipo)\s+of\s+([A-Z][A-Za-z\s&]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_message)
        if match:
            return match.group(1).strip()
    
    # Fallback: look for capitalized words (potential company names)
    words = user_message.split()
    for i, word in enumerate(words):
        if word[0].isupper() and len(word) > 2 and word not in ['I', 'Should', 'Is', 'What', 'How', 'The', 'A', 'An']:
            return word
    
    return None

def fetch_and_calculate_financial_data(user_message, company_name):
    """Fetch financial data and perform calculations using AI."""
    try:
        # First, get the financial data from AI
        data_fetch_prompt = f"""You are a financial data analyst. For the query: "{user_message}"

Company/Stock: {company_name if company_name else "mentioned in query"}

TASK: Fetch and calculate the following financial metrics. If you don't have real-time data, use the most recent data you know or indicate it's hypothetical for demonstration:

1. **Stock Price**: Current trading price
2. **P/E Ratio**: Calculate Price-to-Earnings ratio
3. **P/B Ratio**: Calculate Price-to-Book ratio
4. **Debt-to-Equity**: Calculate debt to equity ratio
5. **Market Cap**: Current market capitalization
6. **EPS (Earnings Per Share)**: Calculate EPS
7. **Revenue Growth**: Year-over-year percentage
8. **Profit Margin**: Calculate net profit margin
9. **ROE (Return on Equity)**: Calculate ROE
10. **52-Week High/Low**: Price range
11. **Industry Average P/E**: For comparison
12. **Dividend Yield**: If applicable

Return the data in this EXACT format:
```
FINANCIAL DATA:
Stock Price: ₹XXX
P/E Ratio: XX.XX (Industry Avg: XX.XX)
P/B Ratio: X.XX
Debt-to-Equity: X.XX
Market Cap: ₹XX,XXX Cr
EPS: ₹XX.XX
Revenue Growth (YoY): XX%
Profit Margin: XX%
ROE: XX%
52-Week Range: ₹XXX - ₹XXX
Dividend Yield: X.XX%
```

Note: If you don't have current real-time data, mention "Data as of [date]" or "Estimated/Historical data for demonstration"."""

        response = requests.post(
            url=API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": API_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial data analyst who provides financial metrics and calculations."
                    },
                    {
                        "role": "user",
                        "content": data_fetch_prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 800
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return None
            
    except Exception as e:
        print(f"Data fetch error: {str(e)}")
        return None

def analyze_calculated_data(user_message, company_name, financial_data):
    """Analyze the calculated financial data and provide insights."""
    try:
        analysis_prompt = f"""You are a financial analyst. Based on the following CALCULATED financial data, provide a comprehensive analysis.

User Query: {user_message}
Company: {company_name if company_name else "mentioned"}

{financial_data}

Now provide a detailed analysis:

1. **📊 Financial Metrics Interpretation**:
   - What does the P/E ratio tell us? (Is it high/low compared to industry?)
   - P/B ratio analysis (Overvalued or undervalued?)
   - Debt levels assessment (Is the debt manageable?)
   - Profitability analysis (Strong or weak margins?)
   - Growth indicators (Revenue and EPS trends)

2. **✅ POSITIVE FACTORS**:
   - List strengths based on the data
   - What looks good about this investment?

3. **⚠️ RISK FACTORS**:
   - List concerns based on the data
   - What should investors be cautious about?

4. **💡 VALUATION ASSESSMENT**:
   - Is it OVERVALUED, FAIRLY VALUED, or UNDERVALUED?
   - Explain your reasoning based on the metrics

5. **🎯 INVESTOR PROFILE SUITABILITY**:
   - Best for: Conservative/Moderate/Aggressive investors?
   - Investment horizon: Short-term/Long-term?

6. **📋 SUGGESTED ACTION PLAN**:
   - What additional research should be done?
   - Key things to monitor
   - When might be a good time to consider (not a direct recommendation)

7. **🔍 WHAT TO VERIFY**:
   - Where to find official data
   - Red flags to watch for
   - Recent news to check

Important: Provide educational analysis, NOT direct buy/sell advice. Be specific about the numbers shown."""

        response = requests.post(
            url=API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": API_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial education expert who analyzes financial data and provides educational insights, not investment advice."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return "Unable to generate detailed analysis."
            
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return "Unable to generate detailed analysis."

def get_financial_analysis_from_api(user_message, company_name=None):
    """Comprehensive financial analysis with data fetching and calculations."""
    try:
        # Step 1: Fetch and calculate financial data
        print("Step 1: Fetching financial data...")
        financial_data = fetch_and_calculate_financial_data(user_message, company_name)
        
        if not financial_data:
            return get_generic_investment_guidance()
        
        # Step 2: Analyze the calculated data
        print("Step 2: Analyzing financial data...")
        analysis = analyze_calculated_data(user_message, company_name, financial_data)
        
        # Step 3: Combine data and analysis
        final_response = f"""# 📈 Investment Analysis Report

## Query: {user_message}

---

## 📊 CALCULATED FINANCIAL METRICS

{financial_data}

---

## 🔍 DETAILED ANALYSIS

{analysis}

---

## ⚠️ IMPORTANT DISCLAIMERS

**This analysis is for educational purposes only and NOT financial advice.**

✓ All metrics should be verified from official sources (NSE, BSE, company filings)
✓ Market conditions change rapidly - data may be outdated
✓ Past performance does not guarantee future returns
✓ Consult a SEBI-registered financial advisor before investing
✓ Only invest money you can afford to lose
✓ Do your own thorough research (DYOR)

## 📚 VERIFY DATA AT:
- **Official**: NSE.com, BSE.com, Company Investor Relations
- **Analysis**: Screener.in, Moneycontrol, TradingView
- **News**: Economic Times, Bloomberg, Reuters
- **Regulatory**: SEBI, Company Annual Reports"""
        
        return final_response
        
    except Exception as e:
        print(f"Financial analysis error: {str(e)}")
        return get_generic_investment_guidance()

def get_generic_investment_guidance():
    """Provide generic investment guidance when API fails."""
    return """📊 **Investment Analysis Framework**

I can help you analyze investment opportunities! However, I need to provide some important guidance:

� **Key Financial Metrics to Research:**

**Fundamental Analysis:**
- **P/E Ratio**: Stock price ÷ Earnings per share (compare to industry average)
- **P/B Ratio**: Market value ÷ Book value (lower may indicate undervaluation)
- **Debt-to-Equity**: Total debt ÷ Shareholder equity (lower is generally better)
- **ROE (Return on Equity)**: Net income ÷ Shareholder equity (higher is better)
- **Profit Margins**: Net profit ÷ Revenue (shows profitability)
- **Revenue Growth**: Year-over-year revenue increase

**For IPOs:**
- Grey Market Premium (GMP)
- Subscription rates
- Use of proceeds
- Promoter background
- Lock-in periods

📈 **How to Evaluate Investment Timing:**

1. **Research the Company**: Read annual reports, quarterly results, management commentary
2. **Industry Analysis**: Understand sector trends and competitive landscape
3. **Valuation Check**: Is the stock overvalued or undervalued compared to peers?
4. **Technical Indicators**: Look at price trends, support/resistance levels
5. **Market Conditions**: Consider overall economic and market sentiment

💡 **Where to Find Data:**
- **Screener.in**: Comprehensive financial ratios
- **Moneycontrol/ET**: News and analysis
- **NSE/BSE**: Official stock data
- **Company websites**: Investor relations section for filings

⚠️ **Critical Reminders:**
1. Never invest based solely on tips or recommendations
2. Diversify your portfolio across sectors
3. Only invest money you can afford to lose
4. Set stop-loss limits to manage risk
5. Consult a SEBI-registered financial advisor
6. Do thorough research before any investment decision

Would you like me to analyze a specific company or investment? Please provide the company name or more details, and I'll help you understand what factors to consider!"""

def chat_with_ai(user_message, context="", conversation_history=None):
    """Send a message to the AI using local GGUF model."""
    try:
        # Check if this is a portfolio recommendation request
        if check_portfolio_query(user_message):
            print(f"Portfolio query detected: {user_message}")
            params = extract_portfolio_parameters(user_message)
            print(f"Extracted parameters: {params}")
            return generate_portfolio_recommendation(user_message, params)
        
        # Check if this is a general investment query
        if check_investment_query(user_message):
            print(f"Investment query detected: {user_message}")
            company_name = extract_company_name(user_message)
            if company_name:
                print(f"Analyzing investment for: {company_name}")
            return get_financial_analysis_from_api(user_message, company_name)
        
        # Load the model for general queries
        model = load_model()
        
        # Build the prompt
        prompt = ""
        
        # Add system message with context
        if context:
            prompt += f"You are a helpful AI assistant. Use the following information from the knowledge base to answer questions:\n\n{context}\n\n"
        
        # Add conversation history (keep last 3 exchanges to manage context)
        if conversation_history and len(conversation_history) > 0:
            recent_history = conversation_history[-6:]  # Last 3 user+assistant pairs
            for msg in recent_history:
                if msg['role'] == 'user':
                    prompt += f"User: {msg['content']}\n"
                elif msg['role'] == 'assistant':
                    prompt += f"Assistant: {msg['content']}\n"
        
        # Add current user message
        prompt += f"User: {user_message}\nAssistant:"
        
        # Generate response
        response = model(
            prompt,
            max_tokens=512,  # Maximum response length
            temperature=0.7,
            top_p=0.9,
            stop=["User:", "\n\n\n"],  # Stop sequences
            echo=False
        )
        
        # Extract the generated text
        return response['choices'][0]['text'].strip()
    
    except FileNotFoundError as e:
        return f"❌ Model Error: {str(e)}"
    except Exception as e:
        print(f"Model Exception: {str(e)}")
        return f"❌ Error generating response: {str(e)}"

@app.route('/')
def index():
    """Render the main chat interface."""
    # Initialize session
    if 'conversation' not in session:
        session['conversation'] = []
    
    # Load documents
    documents = read_documents_from_folder(DATA_FOLDER)
    doc_count = len(documents)
    doc_names = [doc['filename'] for doc in documents]
    
    return render_template('index.html', 
                         doc_count=doc_count, 
                         doc_names=doc_names)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Load documents and create context
    documents = read_documents_from_folder(DATA_FOLDER)
    context = create_context_from_documents(documents)
    
    # Get conversation history from session
    if 'conversation' not in session:
        session['conversation'] = []
    
    conversation_history = session['conversation']
    
    # Get AI response
    ai_response = chat_with_ai(user_message, context, conversation_history)
    
    # Update conversation history
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": ai_response})
    
    # Keep only last 10 messages to prevent context overflow
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    
    session['conversation'] = conversation_history
    session.modified = True
    
    return jsonify({
        'response': ai_response,
        'doc_count': len(documents)
    })

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history."""
    session['conversation'] = []
    session.modified = True
    return jsonify({'status': 'success'})

@app.route('/reload', methods=['POST'])
def reload_documents():
    """Reload documents from data folder."""
    documents = read_documents_from_folder(DATA_FOLDER)
    doc_names = [doc['filename'] for doc in documents]
    return jsonify({
        'status': 'success',
        'doc_count': len(documents),
        'doc_names': doc_names
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
