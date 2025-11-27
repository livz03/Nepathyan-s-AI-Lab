from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.database.connection import db
import socketio

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# Routers
from backend.modules.auth.routes import router as auth_router
from backend.modules.face.routes import router as face_router
from backend.modules.attendance.routes import router as attendance_router

from backend.modules.ai.routes import router as ai_router
from backend.modules.analytics.routes import router as analytics_router
from backend.modules.admin.routes import router as admin_router

app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth")
app.include_router(face_router, prefix=f"{settings.API_PREFIX}/face")
app.include_router(attendance_router, prefix=f"{settings.API_PREFIX}/attendance")

app.include_router(ai_router, prefix=f"{settings.API_PREFIX}/ai")
app.include_router(analytics_router, prefix=f"{settings.API_PREFIX}/analytics")
app.include_router(admin_router, prefix=f"{settings.API_PREFIX}/admin")

@app.on_event("startup")
async def startup_db_client():
    db.connect()
    from backend.seed_db import seed_admin
    await seed_admin()

@app.on_event("shutdown")
async def shutdown_db_client():
    db.close()

@app.get("/")
async def root():
    return {"message": "Welcome to Cortex AI Attendance System"}

# Mount Socket.IO app (Note: Uvicorn should run 'socket_app' if using pure ASGI, 
# but for simplicity in development we often just run 'app' and mount socketio differently 
# or use a specific runner. Here we return app, but in production setup might need adjustment)
# For now, we will expose 'app' and handle socketio via mounting if needed or separate process.
# Actually, wrapping it is better:
app = socketio.ASGIApp(sio, app)
