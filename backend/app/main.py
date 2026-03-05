"""
Main FastAPI Application
Entry point for the Resume Builder API
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router
from backend.app.core.config import settings
import os


# Validate configuration on startup
try:
    settings.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please set GEMINI_API_KEY in your .env file")
    exit(1)


# Initialize FastAPI app
app = FastAPI(
    title="AI Resume Builder API",
    description="Production-grade AI-powered ATS-friendly resume generation system",
    version="1.0.0",
    debug=settings.DEBUG
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(router, prefix="/api", tags=["Resume Builder"])


# Get the absolute path to the frontend directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
frontend_path = os.path.join(project_root, "frontend")


# Mount static files - ✅ FIXED LINE 47
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
app.mount("/pages", StaticFiles(directory=os.path.join(frontend_path, "pages")), name="pages")  # ← REMOVED html=True
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")  # ← ADD THIS LINE


# Serve index.html at root
from fastapi.responses import FileResponse


@app.get("/")
async def read_root():
    """Serve the home page"""
    index_path = os.path.join(frontend_path, "index.html")
    return FileResponse(index_path)


@app.get("/favicon.ico")
async def favicon():
    """Return 204 No Content for favicon requests"""
    from fastapi.responses import Response
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
