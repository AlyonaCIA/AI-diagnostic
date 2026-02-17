"""
File: app/main.py
Description: Main entry point for the AI Diagnostic API. 
Integrates deterministic regex parsing with LLM-powered reasoning 
to provide actionable fixes for PLC build errors.
"""

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Standard Library Imports
from typing import Dict, Any

# Third-Party Imports
from fastapi import FastAPI, HTTPException
from loguru import logger

# Internal Imports
from app.core.parser import PLCParser
from app.utils.xml_manager import XMLContextExtractor
from app.agents.diagnostician import PLCDiagnosticAgent
from app.agents.schemas import DiagnosticReport

# Initialize Singletons at module level for performance optimization
app = FastAPI(title="AI PLC Diagnostic API")
parser = PLCParser()
agent = PLCDiagnosticAgent()


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and orchestration.
    
    Returns:
        status: "healthy" if system is operational
        version: API version
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "AI PLC Diagnostic API"
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health() -> Dict[str, Any]:
    """
    Detailed health check with component status.
    
    Checks:
    - Parser availability
    - LLM provider configuration
    - XML processor readiness
    
    Returns:
        Dictionary with component statuses
    """
    try:
        logger.info("Detailed health check requested")
        
        # Test parser
        test_log = "test error"
        parser_ok = parser.get_metadata(test_log) is not None
        
        # Test LLM provider
        llm_ok = agent.provider is not None
        
        return {
            "status": "healthy" if (parser_ok and llm_ok) else "degraded",
            "version": "0.1.0",
            "components": {
                "parser": "operational" if parser_ok else "failed",
                "llm_provider": "operational" if llm_ok else "failed",
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/classify", response_model=DiagnosticReport)
async def classify_error(payload: Dict[str, str]) -> DiagnosticReport:
    """
    POST /classify
    
    Submits an error log and project XML to get classification and fix suggestions [cite: 27-28].
    Target response time: < 3 seconds per request[cite: 29].
    
    Pipeline Steps:
    1. Error Log Parser: Extract stage and line number [cite: 10-12].
    2. Context Extractor: Fetch relevant XML snippet (POU context)[cite: 8, 12].
    3. Fix Suggestion System: Use LLM for root cause and actionable code snippets [cite: 21-24].
    """
    log_text = payload.get("log_text")
    xml_content = payload.get("xml_content")

    # 1. Validation Guardrail 
    if not log_text or not xml_content:
        logger.error("Request rejected: missing log_text or xml_content.")
        raise HTTPException(
            status_code=400, 
            detail="Payload must include 'log_text' and 'xml_content'."
        )

    logger.info("Starting build error diagnostic pipeline.")

    # 2. Step 1: Parser (Deterministic Metadata Extraction) [cite: 11-12]
    # We identify severity (blocking/warning/info) and build stage [cite: 16-17]
    metadata = parser.get_metadata(log_text)
    logger.debug(f"Parser identification: Stage={metadata['stage']}, Line={metadata['line']}")

    # 3. Step 2: Context Enrichment (XML Parsing) [cite: 12, 25]
    try:
        xml_extractor = XMLContextExtractor(xml_content)
        # We focus context on the 'program0' POU to optimize LLM performance
        context_snippet = xml_extractor.get_pou_context(pou_name="program0")
    except Exception as e:
        logger.warning(f"Graceful context handling: {e}. Analyzing log without XML.")
        context_snippet = "Context missing: Malformed project XML."

    # 4. Step 3: LLM Diagnostic Invisibility (Fix Generation) [cite: 19, 21-24]
    try:
        # Generate 1-3 suggestions with code snippets and confidence scores [cite: 22, 24]
        diagnostic_report = agent.get_fix_suggestions(metadata, context_snippet)
    except Exception as e:
        logger.critical(f"LLM failure: {e}")
        raise HTTPException(
            status_code=500, 
            detail="The AI diagnostic engine failed to generate suggestions."
        )

    logger.success(f"Classification success: {metadata['stage']}. Metadata & Fixes ready.")
    
    return diagnostic_report