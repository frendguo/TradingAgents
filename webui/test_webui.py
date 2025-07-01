#!/usr/bin/env python3
"""
Test script for TradingAgents WebUI
"""
import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test FastAPI imports
        import fastapi
        import uvicorn
        import websockets
        import pydantic
        print("✅ FastAPI dependencies available")
        
        # Test TradingAgents imports
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        print("✅ TradingAgents core modules available")
        
        # Test WebUI backend import
        from webui.backend.main import app
        print("✅ WebUI backend module available")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_api_routes():
    """Test API route definitions"""
    print("\n🧪 Testing API routes...")
    
    try:
        from webui.backend.main import app
        
        expected_routes = [
            "/health",
            "/api/config", 
            "/api/analysis/start",
            "/api/analysis/{analysis_id}",
            "/api/analysis/history"
        ]
        
        actual_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                actual_routes.append(route.path)
        
        missing_routes = []
        for expected in expected_routes:
            if expected not in actual_routes:
                missing_routes.append(expected)
        
        if missing_routes:
            print(f"❌ Missing routes: {missing_routes}")
            return False
        else:
            print("✅ All expected API routes defined")
            return True
            
    except Exception as e:
        print(f"❌ Route test error: {e}")
        return False

def test_config_integration():
    """Test TradingAgents config integration"""
    print("\n🧪 Testing config integration...")
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        required_keys = [
            'llm_provider',
            'deep_think_llm', 
            'quick_think_llm',
            'backend_url'
        ]
        
        missing_keys = []
        for key in required_keys:
            if key not in DEFAULT_CONFIG:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ Missing config keys: {missing_keys}")
            return False
        else:
            print("✅ Config integration successful")
            return True
            
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

def test_frontend_build():
    """Test frontend build artifacts"""
    print("\n🧪 Testing frontend build...")
    
    frontend_dist = project_root / "webui" / "frontend" / "dist"
    
    if not frontend_dist.exists():
        print("❌ Frontend dist directory not found")
        return False
    
    required_files = ["index.html"]
    missing_files = []
    
    for file in required_files:
        if not (frontend_dist / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing frontend files: {missing_files}")
        return False
    else:
        print("✅ Frontend build artifacts present")
        return True

def test_docker_configs():
    """Test Docker configuration files"""
    print("\n🧪 Testing Docker configurations...")
    
    docker_files = [
        "docker-compose.yml",
        "Dockerfile.backend", 
        "Dockerfile.frontend",
        "dokploy.yaml"
    ]
    
    missing_files = []
    for file in docker_files:
        if not (project_root / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing Docker files: {missing_files}")
        return False
    else:
        print("✅ Docker configuration files present")
        return True

def test_environment_setup():
    """Test environment variable setup"""
    print("\n🧪 Testing environment setup...")
    
    # Check for .env.example
    env_example = project_root / ".env.example"
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    # Check README files
    webui_readme = project_root / "webui" / "README.md"
    if not webui_readme.exists():
        print("❌ WebUI README.md not found")
        return False
    
    print("✅ Environment setup files present")
    return True

async def test_async_functionality():
    """Test async functionality"""
    print("\n🧪 Testing async functionality...")
    
    try:
        # Test WebSocket service import
        from webui.frontend.src.services.websocket import WebSocketService
        print("❌ WebSocket service is TypeScript, cannot import in Python")
        return True  # This is expected
    except:
        # This is expected since it's TypeScript
        pass
    
    # Test async route handlers
    try:
        from webui.backend.main import run_analysis, send_websocket_update
        print("✅ Async backend functions available")
        return True
    except Exception as e:
        print(f"❌ Async test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TradingAgents WebUI Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_api_routes,
        test_config_integration,
        test_frontend_build,
        test_docker_configs,
        test_environment_setup,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Async test
    try:
        async_result = asyncio.run(test_async_functionality())
        results.append(async_result)
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    if passed < total:
        print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! WebUI is ready for deployment.")
        print("\n📋 Next Steps:")
        print("1. Set up environment variables (copy .env.example to .env)")
        print("2. Deploy using Docker: docker-compose up --build")
        print("3. Or deploy to DokPloy using dokploy.yaml")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())