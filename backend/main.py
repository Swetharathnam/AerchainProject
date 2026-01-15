from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from contextlib import asynccontextmanager
from database import create_db_and_tables
from routers import rfps, vendors, proposals
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Aerchain RFP System", lifespan=lifespan)
app.include_router(rfps.router)
app.include_router(vendors.router)
app.include_router(proposals.router)

# CORS Configuration
origins = [
    "http://localhost:5173", # Vite Frontend
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Aerchain RFP Backend is running"}

@app.get("/")
def read_root():
    return {"message": "Welcome to Aerchain RFP System API. Visit /docs for Swagger UI."}
