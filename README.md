# FinBot Pioneer 🚀# AI Chatbot - Web Interface



**Your Intelligent Investment Assistant for Indian Markets**A beautiful, modern web interface for your AI chatbot with RAG (Retrieval-Augmented Generation) capabilities using a **local GGUF model**.



A sophisticated AI-powered chatbot that provides personalized investment portfolio recommendations, financial analysis, and market insights tailored for Indian investors.## 🌟 Features



---### User Interface

- **Modern Dark Theme** - Sleek, professional design with gradient accents

## ✨ Features- **Real-time Chat** - Smooth animations and typing indicators

- **Responsive Design** - Works on desktop, tablet, and mobile devices

### 🎯 **Portfolio Builder**- **Smart Suggestions** - Quick-start suggestions for new users

- Generate personalized investment portfolios based on:- **Message History** - Maintains conversation context across messages

  - Capital amount (Lakhs/Crores)

  - Monthly SIP/investment capacity### Functionality

  - Risk appetite (Low/Medium/High)- **Local AI Model** - Uses GGUF models running on your machine (no API costs!)

  - Investment preferences (Mutual Funds, Stocks, Debt, Gold)- **Document Management** - Upload and manage knowledge base documents

- Get detailed recommendations with:- **Live Reload** - Reload documents without restarting the server

  - **Asset Allocation**: Equity, Debt, Gold, Emergency Fund- **Context-Aware Responses** - AI uses your documents + general knowledge

  - **5-7 Specific Mutual Funds**: Real Indian fund names (HDFC, Axis, Parag Parikh, etc.)- **Clear Chat** - Start fresh conversations anytime

  - **8-10 Stock Picks**: NSE/BSE listed companies with sector diversification- **Session Management** - Maintains conversation context

  - **Debt Instruments**: Specific debt funds, bank FDs, government bonds

  - **Gold Investments**: ETFs and Sovereign Gold Bonds## 🚀 Quick Start

  - **Projected Returns**: 5-year CAGR estimates

  - **Monthly SIP Plan**: Detailed distribution of monthly investments### 1. Install Dependencies:

  - **Action Plan**: Where to invest (Zerodha, Groww, etc.)```powershell

pip install -r requirements.txt

### 📊 **Stock Analysis**```

- Comprehensive financial analysis for any Indian stock/company

- AI calculates and explains key metrics:### 2. Add Your GGUF Model:

  - P/E Ratio (Price-to-Earnings)- Download a GGUF model from [Hugging Face](https://huggingface.co/models?search=gguf)

  - P/B Ratio (Price-to-Book)- Rename it to `model.gguf`

  - Debt-to-Equity Ratio- Place it in the `model` folder

  - Revenue Growth & Profit Margins

  - EPS (Earnings Per Share)**Recommended models:**

  - ROE (Return on Equity)- **Llama 3.2 3B**: https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF

- Valuation assessment (Overvalued/Undervalued)- **Phi-3 Mini**: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf

- Risk factors and opportunities- **Mistral 7B**: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

- Investment timing indicators

### 3. Add Your Documents:

### 📚 **Knowledge Base Integration (RAG)**- Place text files, markdown files, or other documents in the `data` folder

- Upload your own documents to the `data` folder- Supported formats: `.txt`, `.md`, `.json`, `.csv`

- AI uses document context to provide informed answers

- Supports: `.txt`, `.md`, `.json`, `.csv` files### 4. Run the Web Application:

```powershell

### 💡 **Educational Guidance**python app.py

- Answers general investment questions```

- Explains financial concepts and metrics

- Provides resources and tools for research### 5. Open Your Browser:

- Safe recommendations without direct buy/sell advice- Navigate to: `http://localhost:5000`

- Start chatting!

---

## 📁 Project Structure

## 🚀 Quick Start

```

### 1. **Install Dependencies**├── app.py                  # Flask web application

```bash├── chatbot.py             # CLI version (optional)

pip install -r requirements.txt├── requirements.txt       # Python dependencies

```├── data/                  # Knowledge base documents

│   └── example.txt

### 2. **Add Your Documents** (Optional)├── templates/             # HTML templates

Place any knowledge base files in the `data` folder:│   └── index.html

```└── static/                # Static assets

data/    ├── css/

  └── your-documents.txt    │   └── style.css

```    └── js/

        └── script.js

### 3. **Add GGUF Model** (Optional for non-investment queries)```

- Download a GGUF model from [Hugging Face](https://huggingface.co/models?search=gguf)

- Rename it to `model.gguf`## 🎨 Interface Components

- Place in the `model` folder

### Sidebar

**Recommended models:**- **Knowledge Base Info** - Shows loaded documents count

- [Llama 3.2 3B](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF)- **Document List** - Lists all loaded files

- [Phi-3 Mini](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)- **Model Information** - Displays AI model details

- **Quick Actions** - Reload documents, clear chat

### 4. **Run the Application**

```bash### Chat Area

python app.py- **Welcome Screen** - Greeting and suggestions for new users

```- **Message Display** - User and AI messages with timestamps

- **Typing Indicator** - Shows when AI is processing

### 5. **Access the Web Interface**- **Input Area** - Text input with auto-resize

- **Local**: http://127.0.0.1:5000

- **LAN**: http://YOUR_LOCAL_IP:5000## ⌨️ Keyboard Shortcuts



---- `Enter` - Send message

- `Shift + Enter` - New line in message

## 💬 Example Queries- `Ctrl/Cmd + R` - Reload page



### Portfolio Recommendations:## 🔧 Configuration

```

"Create a portfolio for 10 lakhs with medium risk in mutual funds and stocks"Edit `app.py` to customize:

- `API_KEY` - Your OpenRouter API key

"I have 5 lakhs and can invest 20,000 monthly. Low risk. Suggest debt and balanced funds"- `MODEL` - AI model to use

- `DATA_FOLDER` - Location of knowledge base documents

"Build me an aggressive portfolio with 20 lakhs capital"- `PORT` - Web server port (default: 5000)



"Suggest diversified portfolio for 15 lakhs with SIP of 30,000"## 💡 Usage Tips

```

1. **Add Quality Documents** - Better documents = better answers

### Stock Analysis:2. **Use Clear Filenames** - Helps identify document sources

```3. **Reload After Changes** - Click "Reload Documents" after adding files

"Should I invest in Reliance?"4. **Clear Chat for New Topics** - Start fresh for different discussions

5. **Use Suggestions** - Click suggestion chips to get started

"Analyze TCS stock for me"

## 🌐 API Endpoints

"Is Infosys a good investment right now?"

- `GET /` - Main chat interface

"What do you think about HDFC Bank shares?"- `POST /chat` - Send message and get response

```- `POST /clear` - Clear conversation history

- `POST /reload` - Reload documents from data folder

### General Investment Questions:- `GET /health` - Health check

```

"What are the best mutual funds for 2024?"## 🎯 Features Showcase



"Explain P/E ratio and P/B ratio"### Real-time Communication

- Instant message sending

"How to choose stocks for long-term investment?"- Typing indicators

- Smooth animations

"Difference between debt funds and equity funds"

```### Knowledge Base Integration

- Automatic document loading

---- Multi-file support

- Context-aware responses

## 📁 Project Structure

### User Experience

```- Beautiful gradients and colors

FinBot-Pioneer/- Intuitive interface

├── app.py                 # Flask web application- Mobile-responsive design

├── chatbot.py            # CLI version (optional)- Accessibility features

├── requirements.txt      # Python dependencies

├── README.md             # This file## 🔒 Security Notes

├── data/                 # Knowledge base documents

│   └── example.txt- API key is stored in `app.py` - keep it secure!

├── model/                # GGUF model folder- Use environment variables for production

│   └── README.md- Enable HTTPS for production deployment

├── templates/            # HTML templates- Add authentication if deploying publicly

│   └── index.html

└── static/               # Frontend assets## 📱 Browser Support

    ├── css/

    │   └── style.css- Chrome/Edge (recommended)

    └── js/- Firefox

        └── script.js- Safari

```- Opera



---## 🐛 Troubleshooting



## 🔧 Configuration**Port already in use?**

```powershell

### API Settings (in `app.py`):# Change port in app.py or kill existing process

```python```

API_KEY = "your-openrouter-api-key"

API_MODEL = "openai/gpt-4o-mini"**Documents not loading?**

API_URL = "https://openrouter.ai/api/v1/chat/completions"- Check file formats (must be .txt, .md, .json, or .csv)

```- Verify files are in the `data` folder

- Click "Reload Documents" button

### Data Folder:

- Add documents to `data/` folder**API errors?**

- Supported formats: `.txt`, `.md`, `.json`, `.csv`- Verify API key is correct

- Click "Reload Documents" in the web interface after adding files- Check internet connection

- Ensure OpenRouter service is available

---

## 🚀 Production Deployment

## 🌐 Access from Other Devices (LAN)

For production use:

The server runs on all network interfaces, making it accessible from any device on your local network:1. Set `debug=False` in `app.py`

2. Use environment variables for secrets

1. **Find your local IP**: Check the terminal output when starting the server3. Use a production WSGI server (gunicorn, waitress)

2. **Share the URL**: `http://YOUR_LOCAL_IP:5000`4. Enable HTTPS

3. **Access from phones/tablets**: Connect to same WiFi and open the URL5. Add authentication/authorization

6. Implement rate limiting

**Firewall Setup** (if needed):

```powershell## 📝 License

netsh advfirewall firewall add rule name="FinBot Pioneer" dir=in action=allow protocol=TCP localport=5000

```This project is open source and available for personal and commercial use.

*(Run PowerShell as Administrator)*

---

---

Built with ❤️ using Flask, OpenRouter AI, and modern web technologies

## 🎨 Features Breakdown

### Investment Portfolio Generation
- ✅ Accepts capital amount in various formats (Lakhs/Crores)
- ✅ Extracts risk appetite automatically
- ✅ Provides sector-wise diversification
- ✅ Includes actual Indian mutual fund names
- ✅ Real NSE/BSE stock symbols
- ✅ Bank recommendations for FDs
- ✅ Gold investment options (ETFs, SGBs)
- ✅ Projected returns with multiple scenarios

### Financial Analysis
- ✅ Fetches and calculates financial metrics using AI
- ✅ Explains complex ratios in simple terms
- ✅ Industry comparisons
- ✅ Valuation assessment
- ✅ Risk analysis
- ✅ Investment timing suggestions

### Smart Detection
- 🤖 Automatically detects portfolio requests
- 📊 Identifies stock analysis queries
- 💼 Recognizes general investment questions
- 📚 Falls back to document context for other queries

---

## ⚠️ Important Disclaimers

**FinBot Pioneer is for educational purposes only.**

- ✓ Not financial advice - Consult SEBI-registered advisors
- ✓ AI-generated recommendations based on training data
- ✓ Verify all data from official sources (NSE, BSE, AMC websites)
- ✓ Markets are subject to risk - Read all scheme documents
- ✓ Past performance ≠ future results
- ✓ Understand tax implications before investing
- ✓ Only invest money you can afford to lose

---

## 📚 Official Resources

- **Mutual Funds**: [AMFI India](https://www.amfiindia.com)
- **Stocks**: [NSE](https://www.nseindia.com) | [BSE](https://www.bseindia.com)
- **Regulatory**: [SEBI](https://www.sebi.gov.in)
- **Analysis**: [Screener.in](https://www.screener.in) | [Value Research](https://www.valueresearchonline.com)
- **Investment Platforms**: Zerodha, Groww, Paytm Money, Kuvera

---

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **AI**: OpenRouter API (GPT-4o-mini)
- **Local AI**: llama-cpp-python (GGUF models)
- **Frontend**: HTML, CSS, JavaScript
- **RAG**: Document-based context retrieval

---

## 📝 Requirements

```
flask==3.0.0
requests==2.31.0
llama-cpp-python==0.2.90
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py or kill existing process
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

### Documents Not Loading
- Check file formats (must be .txt, .md, .json, or .csv)
- Verify files are in the `data` folder
- Click "Reload Documents" button in the UI

### API Errors
- Verify API key is correct in `app.py`
- Check internet connection
- Ensure OpenRouter service is available

### Model Not Found (for general queries)
- Add a GGUF model file to the `model` folder
- Rename it to `model.gguf`
- For investment queries, model is not required (uses API)

---

## 🎯 Use Cases

1. **New Investors**: Get started with guided portfolio recommendations
2. **Portfolio Rebalancing**: Analyze current holdings and get suggestions
3. **Research Tool**: Quickly analyze multiple stocks and mutual funds
4. **Learning**: Understand financial metrics and investment concepts
5. **Planning**: Calculate projected returns for different scenarios
6. **Comparison**: Compare different investment strategies

---

## 🚀 Future Enhancements

- [ ] Real-time market data integration
- [ ] Portfolio tracking and performance monitoring
- [ ] Tax calculator for LTCG/STCG
- [ ] Comparison tools for multiple funds/stocks
- [ ] News integration for market updates
- [ ] User authentication and saved portfolios
- [ ] Mobile app version

---

## 📄 License

This project is for educational and personal use.

---

## 🤝 Contributing

This is a hackathon project. Feel free to fork and enhance!

---

## 📧 Support

For issues or questions, check the terminal logs for error messages.

---

**Built with ❤️ for Indian Investors**

*FinBot Pioneer - Your Intelligent Investment Companion* 🎯📈
