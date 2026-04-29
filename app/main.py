import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.config import settings

# Render da ephemeral (vaqtinchalik) filesystem — restart da fayllar o'chadi
# Avatar upload lokal ishlaydi, production da cloud storage (S3/Cloudinary) tavsiya qilinadi
os.makedirs("uploads/avatars", exist_ok=True)

app = FastAPI(
    title="E-Voting System API",
    version="1.0.0",
    description="Onlayn ovoz berish uchun API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# uploads papkasi mavjud bo'lsa mount qiladi
if os.path.isdir("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
