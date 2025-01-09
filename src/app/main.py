from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
import uvicorn

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


if __name__ =="__main__":
    uvicorn.run("src.app.main:app", port=8000, reload=True,access_log=True, timeout_keep_alive =2000000000)
