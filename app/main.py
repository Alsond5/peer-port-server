from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from app.domain import RateLimiter, logger
from app.routers import monitoring, signaling

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rate_limiter = RateLimiter()
    app.state.cleanup_task = None
    
    async def cleanup_task():
        while True:
            await asyncio.sleep(60)
            app.state.rate_limiter.cleanup()
            
    app.state.cleanup_task = asyncio.create_task(cleanup_task())
    logger.info("Signaling server starting up")
    
    yield
    
    if app.state.cleanup_task:
        app.state.cleanup_task.cancel()
        try:
            await app.state.cleanup_task
        except asyncio.CancelledError:
            pass

    logger.info("Signaling server shutting down")

app = FastAPI(
    title="WebRTC P2P File Transfer Signaling Server",
    description="A lightweight signaling server for P2P file transfers using WebRTC",
    version="2.0.0",
    lifespan=lifespan
)

origins = [
    "https://peerport.netlify.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(monitoring.router)
app.include_router(signaling.router)

@app.get("/")
async def root():
    return {
        "title": app.title,
        "description": app.description,
        "version": app.version,
    }

@app.get("/health-check")
async def health_check():
    return {
        "status": "ok"
    }