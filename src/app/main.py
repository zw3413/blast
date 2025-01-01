from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI()
# Include the router in the app
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your Vue app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}


