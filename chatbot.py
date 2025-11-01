import requests
import json
import os
from pathlib import Path
import re

# Configuration
API_KEY = "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"
MODEL = "openai/gpt-4o-mini"  # Changed from search-preview to standard model
API_URL = "https://openrouter.ai/api/v1/chat/completions"
DATA_FOLDER = "data"

def read_documents_from_folder(folder_path):
    """Read all text files from the data folder and return their contents."""
    documents = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Creating {folder_path} folder...")
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
                    print(f"Loaded: {file_path.name}")
            except Exception as e:
                print(f"Error reading {file_path.name}: {e}")
    
    return documents

def create_context_from_documents(documents):
    """Create a context string from all documents."""
    if not documents:
        return "No documents found in the data folder."
    
    context = "Here is the information from the knowledge base:\n\n"
    for doc in documents:
        context += f"--- Document: {doc['filename']} ---\n"
        context += doc['content']
        context += "\n\n"
    
    return context

def check_investment_query(user_message):
    """Check if the message is asking for investment advice."""
    investment_keywords = [
        'invest', 'investment', 'stock', 'stocks', 'ipo', 'share', 'shares',
        'buy', 'sell', 'trading', 'trade', 'portfolio', 'equity', 'equities',
        'mutual fund', 'should i buy', 'should i invest', 'good investment',
        'worth investing', 'market', 'bullish', 'bearish', 'nifty', 'sensex'
    ]
    
    message_lower = user_message.lower()
    return any(keyword in message_lower for keyword in investment_keywords)

def extract_company_name(user_message):
    """Extract company/stock name from the message."""
    patterns = [
        r'(?:invest in|buy|sell|about|regarding)\s+([A-Z][A-Za-z\s&]+?)(?:\s+(?:stock|shares|ipo|company))',
        r'([A-Z][A-Za-z\s&]+?)\s+(?:stock|shares|ipo|company)',
        r'(?:stock|shares|ipo)\s+of\s+([A-Z][A-Za-z\s&]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_message)
        if match:
            return match.group(1).strip()
    
    words = user_message.split()
    for word in words:
        if word and word[0].isupper() and len(word) > 2 and word not in ['I', 'Should', 'Is', 'What', 'How', 'The', 'A', 'An']:
            return word
    
    return None

def get_financial_analysis(user_message, company_name=None):
    """Use API to get intelligent financial analysis."""
    try:
        analysis_prompt = f"""You are a financial analysis expert. Analyze the following investment query and provide a comprehensive analysis.

User Query: {user_message}

Please provide:
1. **Company Overview**: Brief background (if specific company mentioned)
2. **Financial Metrics Analysis**: 
   - P/E Ratio interpretation (compare to industry average)
   - P/B Ratio analysis
   - Debt-to-Equity assessment
   - Revenue and profit growth trends
   - EPS trends
3. **Key Factors to Consider**:
   - Industry outlook
   - Competitive position
   - Recent news/developments
   - Risks and opportunities
4. **Investment Timing Indicators**:
   - Current market conditions
   - Technical indicators if relevant
   - Valuation assessment (overvalued/undervalued)
5. **Educational Guidance**:
   - What metrics the investor should research
   - Where to find reliable data
   - Red flags to watch for
6. **Balanced Recommendation Framework**:
   - Pros and cons
   - Risk level assessment
   - Suggested action plan (research steps)

Important: 
- Do NOT give direct "buy" or "sell" advice
- Focus on education and analysis framework
- Mention the need for personal research and professional consultation
- Include disclaimers about investment risks
- If you don't have current data, mention it and suggest where to find it"""

        response = requests.post(
            url=API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial education expert who helps people understand investment analysis. You provide educational guidance, not direct investment advice."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            })
        )
        
        response.raise_for_status()
        result = response.json()
        analysis = result['choices'][0]['message']['content']
        
        analysis += """\n\n---
⚠️ IMPORTANT DISCLAIMER: This analysis is for educational purposes only and should not be considered as financial advice. Always:
- Do your own thorough research
- Consult with a SEBI-registered financial advisor
- Understand that all investments carry risk
- Never invest money you cannot afford to lose
- Verify all data from official sources

📚 RECOMMENDED RESOURCES:
- Screener.in, Moneycontrol, Yahoo Finance
- NSE, BSE, company investor relations pages
- Economic Times, Bloomberg, Reuters"""
        
        return analysis
        
    except Exception as e:
        print(f"Error in financial analysis: {str(e)}")
        return """I encountered an error getting detailed analysis. However, I can guide you on what to research:

Key metrics to check:
- P/E Ratio (Price to Earnings)
- P/B Ratio (Price to Book)
- Debt-to-Equity Ratio
- Revenue Growth (YoY)
- Profit Margins

Resources: Screener.in, Moneycontrol, NSE/BSE websites

Always consult a financial advisor before making investment decisions."""

def chat_with_ai(user_message, context=""):
    """Send a message to the AI and get a response."""
    # Check if this is an investment query
    if check_investment_query(user_message):
        print("\n🔍 Detecting investment query, analyzing...")
        company_name = extract_company_name(user_message)
        if company_name:
            print(f"📊 Analyzing: {company_name}")
        return get_financial_analysis(user_message, company_name)
    
    # Prepare the system message with context
    messages = []
    
    if context:
        system_message = (
            "You are a helpful AI assistant. Use the following information from the knowledge base "
            "to answer the user's question. If the answer is in the knowledge base, use it. "
            "If not, you can use your general knowledge but mention that the information "
            "is not in the provided documents.\n\n"
            f"{context}"
        )
        messages.append({
            "role": "system",
            "content": system_message
        })
    
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Make the API request
    try:
        response = requests.post(
            url=API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "RAG Chatbot",
            },
            data=json.dumps({
                "model": MODEL,
                "messages": messages,
            })
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']
    
    except requests.exceptions.RequestException as e:
        return f"Error communicating with API: {e}"
    except (KeyError, IndexError) as e:
        return f"Error parsing API response: {e}"

def main():
    """Main chatbot loop."""
    print("=" * 60)
    print("AI CHATBOT WITH KNOWLEDGE BASE")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Data folder: {DATA_FOLDER}")
    print("=" * 60)
    
    # Load documents from data folder
    print("\nLoading documents from data folder...")
    documents = read_documents_from_folder(DATA_FOLDER)
    
    if documents:
        print(f"\nLoaded {len(documents)} document(s)!")
        context = create_context_from_documents(documents)
    else:
        print("\nNo documents found. Add files to the 'data' folder for context-aware responses.")
        context = ""
    
    print("\n" + "=" * 60)
    print("Chat started! Type 'exit' or 'quit' to end the conversation.")
    print("Type 'reload' to reload documents from the data folder.")
    print("=" * 60 + "\n")
    
    # Chat loop
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['exit', 'quit']:
            print("\nGoodbye!")
            break
        
        if user_input.lower() == 'reload':
            print("\nReloading documents...")
            documents = read_documents_from_folder(DATA_FOLDER)
            if documents:
                print(f"Loaded {len(documents)} document(s)!")
                context = create_context_from_documents(documents)
            else:
                print("No documents found.")
                context = ""
            continue
        
        print("\nAI: ", end="", flush=True)
        response = chat_with_ai(user_input, context)
        print(response)
        print()

if __name__ == "__main__":
    main()
