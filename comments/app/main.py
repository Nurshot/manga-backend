from fastapi import FastAPI
from .routers import comment_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# CORS Middleware: allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"], 
)
app.include_router(comment_router, prefix="/comments")