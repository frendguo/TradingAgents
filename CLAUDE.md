# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM-powered financial trading framework that simulates real-world trading firms. The system uses specialized agents (analysts, researchers, traders, risk managers) that collaborate to evaluate market conditions and make trading decisions through structured debates and analysis.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
conda create -n tradingagents python=3.13
conda activate tradingagents

# Install dependencies
pip install -r requirements.txt
```

### Required Environment Variables
```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY  # Free tier available
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY    # Required for agents
```

### Running the Application
```bash
# CLI interface
python -m cli.main

# Direct Python usage
python main.py
```

## Architecture Overview

### Core Components

**TradingAgentsGraph** (`tradingagents/graph/trading_graph.py`): Main orchestrator that coordinates all agents and manages the trading workflow.

**Agent Teams**:
- **Analysts** (`tradingagents/agents/analysts/`): Specialized analysis agents
  - `fundamentals_analyst.py`: Company financials and intrinsic value
  - `market_analyst.py`: Market conditions and trends
  - `news_analyst.py`: News and macroeconomic indicators
  - `social_media_analyst.py`: Sentiment analysis from social media
- **Researchers** (`tradingagents/agents/researchers/`): Critical evaluation agents
  - `bull_researcher.py`: Bullish perspective analysis
  - `bear_researcher.py`: Bearish perspective analysis
- **Risk Management** (`tradingagents/agents/risk_mgmt/`): Risk assessment agents
  - `conservative_debator.py`: Conservative risk assessment
  - `aggresive_debator.py`: Aggressive risk assessment
  - `neutral_debator.py`: Neutral risk perspective
- **Trader** (`tradingagents/agents/trader/trader.py`): Final decision maker

**Data Integration** (`tradingagents/dataflows/`): External data sources and utilities
- `finnhub_utils.py`: FinnHub API integration
- `yfin_utils.py`: Yahoo Finance integration
- `reddit_utils.py`: Reddit sentiment data
- `googlenews_utils.py`: Google News integration

**Graph Processing** (`tradingagents/graph/`): LangGraph-based workflow management
- `trading_graph.py`: Main graph orchestration
- `conditional_logic.py`: Decision flow logic
- `propagation.py`: Information flow between agents
- `reflection.py`: Learning and memory systems
- `signal_processing.py`: Signal analysis and processing

### Configuration System

The system uses a centralized configuration in `tradingagents/default_config.py`:
- LLM settings (supports OpenAI, Anthropic, Google)
- Debate rounds and discussion limits
- Data directories and caching
- Online vs offline tool usage

Key configuration options:
```python
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "o4-mini"      # Deep reasoning model
config["quick_think_llm"] = "gpt-4o-mini" # Fast response model
config["max_debate_rounds"] = 1            # Agent debate iterations
config["online_tools"] = True             # Real-time vs cached data
```

### Agent Workflow

1. **Data Collection**: Analysts gather market data using specialized tools
2. **Analysis Phase**: Each analyst provides domain-specific insights
3. **Research Debate**: Bull/bear researchers debate the analysis findings
4. **Risk Assessment**: Risk management team evaluates potential risks
5. **Trading Decision**: Trader agent makes final buy/sell/hold decision
6. **Portfolio Management**: Final approval/rejection of trades

### Memory and Learning

The framework includes a memory system (`tradingagents/agents/utils/memory.py`) that allows agents to:
- Remember past decisions and outcomes
- Learn from trading mistakes
- Adapt strategies based on historical performance

### CLI Interface

The CLI (`cli/main.py`) provides an interactive interface for:
- Selecting tickers and analysis dates
- Configuring LLM models and research depth
- Real-time progress tracking during analysis
- Viewing detailed agent reports and decisions

## Development Notes

- Built with LangGraph for modular agent workflows
- Supports multiple LLM providers (OpenAI, Anthropic, Google)
- Uses both real-time APIs and cached data for backtesting
- Designed for research purposes with extensive debugging capabilities
- Framework makes numerous API calls - use smaller models for testing to manage costs