"""
FastAPI backend for TradingAgents WebUI
"""
import os
import sys
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global analysis storage
analyses: Dict[str, dict] = {}
websocket_connections: Dict[str, WebSocket] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting TradingAgents WebUI Backend")
    yield
    logger.info("Shutting down TradingAgents WebUI Backend")

app = FastAPI(
    title="TradingAgents WebUI API",
    description="Multi-agent LLM trading framework API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AnalysisRequest(BaseModel):
    symbol: str
    date: Optional[str] = None
    llm_provider: str = "openai"
    deep_think_llm: str = "gpt-4o-mini"
    quick_think_llm: str = "gpt-4o-mini"
    backend_url: Optional[str] = None
    max_debate_rounds: int = 1
    online_tools: bool = True

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    created_at: str

class AnalysisResult(BaseModel):
    analysis_id: str
    symbol: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None

class ConfigResponse(BaseModel):
    llm_providers: List[str]
    available_models: Dict[str, List[str]]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Configuration endpoint
@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """Get available configuration options"""
    return ConfigResponse(
        llm_providers=["openai", "anthropic", "google", "deepseek", "openrouter", "ollama"],
        available_models={
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            "google": ["gemini-1.5-pro", "gemini-1.5-flash"],
            "deepseek": ["deepseek-chat", "deepseek-reasoner"],
            "openrouter": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o"],
            "ollama": ["llama3.1", "llama3.2", "qwen3"]
        }
    )

# Start analysis endpoint
@app.post("/api/analysis/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start a new trading analysis"""
    analysis_id = str(uuid.uuid4())
    
    # Create analysis record
    analysis = {
        "analysis_id": analysis_id,
        "symbol": request.symbol,
        "status": "started",
        "created_at": datetime.now().isoformat(),
        "request": request.dict(),
        "progress": [],
        "result": None,
        "error": None
    }
    
    analyses[analysis_id] = analysis
    
    # Start background analysis
    background_tasks.add_task(run_analysis, analysis_id, request)
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="started",
        created_at=analysis["created_at"]
    )

# Get analysis result endpoint
@app.get("/api/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str):
    """Get analysis result by ID"""
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analyses[analysis_id]
    return AnalysisResult(
        analysis_id=analysis_id,
        symbol=analysis["symbol"],
        status=analysis["status"],
        created_at=analysis["created_at"],
        completed_at=analysis.get("completed_at"),
        result=analysis.get("result"),
        error=analysis.get("error")
    )

# Get analysis history endpoint
@app.get("/api/analysis/history")
async def get_analysis_history():
    """Get all analysis history"""
    history = []
    for analysis_id, analysis in analyses.items():
        history.append({
            "analysis_id": analysis_id,
            "symbol": analysis["symbol"],
            "status": analysis["status"],
            "created_at": analysis["created_at"],
            "completed_at": analysis.get("completed_at")
        })
    
    # Sort by creation time (newest first)
    history.sort(key=lambda x: x["created_at"], reverse=True)
    return {"history": history}

# WebSocket endpoint for real-time updates
@app.websocket("/ws/analysis/{analysis_id}")
async def websocket_endpoint(websocket: WebSocket, analysis_id: str):
    """WebSocket endpoint for real-time analysis updates"""
    await websocket.accept()
    websocket_connections[analysis_id] = websocket
    
    try:
        # Send current status if analysis exists
        if analysis_id in analyses:
            analysis = analyses[analysis_id]
            await websocket.send_json({
                "type": "status",
                "status": analysis["status"],
                "progress": analysis.get("progress", [])
            })
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        if analysis_id in websocket_connections:
            del websocket_connections[analysis_id]
        logger.info(f"WebSocket disconnected for analysis {analysis_id}")

async def send_websocket_update(analysis_id: str, message: dict):
    """Send update to WebSocket if connected"""
    if analysis_id in websocket_connections:
        try:
            await websocket_connections[analysis_id].send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            # Remove dead connection
            if analysis_id in websocket_connections:
                del websocket_connections[analysis_id]

async def run_analysis(analysis_id: str, request: AnalysisRequest):
    """Run the trading analysis in background"""
    try:
        analysis = analyses[analysis_id]
        
        # Update status
        analysis["status"] = "running"
        await send_websocket_update(analysis_id, {
            "type": "status",
            "status": "running",
            "message": "Starting analysis..."
        })
        
        # Create config
        config = DEFAULT_CONFIG.copy()
        config.update({
            "llm_provider": request.llm_provider,
            "deep_think_llm": request.deep_think_llm,
            "quick_think_llm": request.quick_think_llm,
            "backend_url": request.backend_url or get_backend_url(request.llm_provider),
            "max_debate_rounds": request.max_debate_rounds,
            "online_tools": request.online_tools,
            "ticker": request.symbol,
            "date": request.date or datetime.now().strftime("%Y-%m-%d")
        })
        
        # Progress tracking
        progress_steps = [
            "Initializing agents...",
            "Collecting market data...",
            "Running fundamental analysis...",
            "Running technical analysis...",
            "Analyzing news and sentiment...",
            "Running bull/bear debate...",
            "Risk assessment...",
            "Making trading decision...",
            "Finalizing report..."
        ]
        
        current_step = 0
        
        # Create and run trading graph
        trading_graph = TradingAgentsGraph(config)
        
        # Custom progress callback
        async def progress_callback(step: str, details: str = ""):
            nonlocal current_step
            if current_step < len(progress_steps):
                progress_msg = progress_steps[current_step]
                current_step += 1
            else:
                progress_msg = step
                
            analysis["progress"].append({
                "step": progress_msg,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
            
            await send_websocket_update(analysis_id, {
                "type": "progress",
                "step": progress_msg,
                "details": details,
                "progress_percent": min(100, (current_step / len(progress_steps)) * 100)
            })
        
        # Mock progress updates (since we can't easily modify the existing graph)
        for i, step in enumerate(progress_steps):
            await progress_callback(step)
            await asyncio.sleep(0.5)  # Small delay for demo
        
        # Run the actual analysis
        logger.info(f"Starting analysis for {request.symbol}")
        result = await asyncio.to_thread(trading_graph.run_analysis)
        
        # Process and store result
        analysis["result"] = {
            "symbol": request.symbol,
            "decision": result.get("final_decision", "HOLD"),
            "confidence": result.get("confidence", 0.5),
            "reasoning": result.get("reasoning", "Analysis completed"),
            "agents_reports": result.get("agents_reports", {}),
            "risk_assessment": result.get("risk_assessment", {}),
            "summary": result.get("summary", "Trading analysis completed successfully")
        }
        
        analysis["status"] = "completed"
        analysis["completed_at"] = datetime.now().isoformat()
        
        # Send completion notification
        await send_websocket_update(analysis_id, {
            "type": "completed",
            "status": "completed",
            "result": analysis["result"]
        })
        
        logger.info(f"Analysis completed for {request.symbol}: {analysis['result']['decision']}")
        
    except Exception as e:
        logger.error(f"Analysis failed for {analysis_id}: {str(e)}")
        
        analysis["status"] = "failed"
        analysis["error"] = str(e)
        analysis["completed_at"] = datetime.now().isoformat()
        
        await send_websocket_update(analysis_id, {
            "type": "error",
            "status": "failed",
            "error": str(e)
        })

def get_backend_url(provider: str) -> str:
    """Get backend URL for LLM provider"""
    urls = {
        "openai": "https://api.openai.com/v1",
        "anthropic": "https://api.anthropic.com/",
        "google": "https://generativelanguage.googleapis.com/v1",
        "deepseek": "https://api.deepseek.com/v1",
        "openrouter": "https://openrouter.ai/api/v1",
        "ollama": "http://localhost:11434/v1"
    }
    return urls.get(provider, "https://api.openai.com/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )