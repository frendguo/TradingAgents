# TradingAgents WebUI

A modern web interface for the TradingAgents multi-agent LLM trading framework.

## Features

- 🚀 **Real-time Analysis**: Live progress tracking with WebSocket updates
- 📊 **Interactive Dashboard**: Rich visualization of trading decisions and agent reports
- 🔧 **Flexible Configuration**: Support for multiple LLM providers and models
- 📈 **Historical Analysis**: View and manage past trading analyses
- 🐳 **Docker Ready**: Easy deployment with Docker and DokPloy

## Architecture

```
webui/
├── backend/          # FastAPI backend
│   ├── main.py       # API server
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API and WebSocket services
│   │   └── types/        # TypeScript definitions
│   └── package.json
├── docker-compose.yml    # Multi-container setup
├── Dockerfile.backend    # Backend container
├── Dockerfile.frontend   # Frontend container
└── dokploy.yaml         # DokPloy deployment config
```

## Quick Start

### Prerequisites

1. **Environment Variables**: Set up API keys
   ```bash
   export FINNHUB_API_KEY=your_finnhub_key
   export OPENAI_API_KEY=your_openai_key
   # Optional: ANTHROPIC_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY
   ```

2. **Dependencies**: Install project dependencies
   ```bash
   pip install -r requirements.txt
   ```

### Development

1. **Start Backend** (Terminal 1):
   ```bash
   cd webui/backend
   PYTHONPATH=../.. python main.py
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd webui/frontend
   npm install
   npm run dev
   ```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Docker Deployment

1. **Build and Run**:
   ```bash
   docker-compose up --build
   ```

2. **Access Application**:
   - Web Interface: http://localhost:80
   - API: http://localhost:80/api

### DokPloy Deployment

1. **Configure Environment**:
   - Update `dokploy.yaml` with your domain
   - Set environment variables in DokPloy

2. **Deploy**:
   ```bash
   # Push to your git repository
   git add . && git commit -m "Deploy WebUI"
   git push origin main
   
   # DokPloy will auto-deploy from git
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/config` | Available models and providers |
| POST | `/api/analysis/start` | Start new analysis |
| GET | `/api/analysis/{id}` | Get analysis result |
| GET | `/api/analysis/history` | Get analysis history |
| WS | `/ws/analysis/{id}` | Real-time progress updates |

## Usage

1. **Start Analysis**:
   - Enter stock symbol (e.g., AAPL, TSLA)
   - Configure LLM provider and models
   - Set analysis parameters
   - Click "Start Analysis"

2. **Monitor Progress**:
   - Real-time progress updates
   - Agent execution steps
   - WebSocket-powered live updates

3. **View Results**:
   - Trading decision (BUY/SELL/HOLD)
   - Confidence score
   - Detailed agent reports
   - Risk assessment

4. **Review History**:
   - Past analysis results
   - Performance statistics
   - Quick access to previous reports

## Configuration

### LLM Providers

Supported providers:
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3.5-sonnet, Claude-3.5-haiku
- **Google**: Gemini-1.5-pro, Gemini-1.5-flash
- **DeepSeek**: deepseek-chat, deepseek-reasoner
- **OpenRouter**: Various models
- **Ollama**: Local models

### Environment Variables

```bash
# Required
FINNHUB_API_KEY=your_finnhub_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Backend Configuration
VITE_API_URL=http://localhost:8000  # Frontend API URL
```

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=/path/to/TradingAgents
   ```

2. **API Key Issues**:
   ```bash
   # Verify environment variables
   echo $FINNHUB_API_KEY
   echo $OPENAI_API_KEY
   ```

3. **WebSocket Connection**:
   - Check firewall settings
   - Ensure WebSocket support in proxy
   - Verify correct WebSocket URL

4. **Docker Issues**:
   ```bash
   # Rebuild containers
   docker-compose down
   docker-compose up --build
   ```

### Development Tips

1. **Hot Reload**: Frontend supports hot reload during development
2. **API Testing**: Use `/docs` endpoint for interactive API testing
3. **Logs**: Check Docker logs for debugging
4. **Database**: SQLite database stored in `./data` volume

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

This project follows the same license as the main TradingAgents project.