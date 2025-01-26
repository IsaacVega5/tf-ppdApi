from fastapi import FastAPI
from fastapi.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes import User

load_dotenv()

origins = [
    "*",
]
middleware = [
  Middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=["*"],
  )
]

app = FastAPI(middleware=middleware)

app.include_router(User.router)

@app.get("/")
async def root():
  return {"message": "You should not be seeing this"}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app)