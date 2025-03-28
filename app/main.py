from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.routes import InstitutionType, User, Institution

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
app.include_router(InstitutionType.router)
app.include_router(Institution.router)


# this defines a max; if a router sets a limit less than this one, then
# the router limit prevails. if a router sets a limit higher than this one,
# the default prevails.
limiter = Limiter(key_func=get_remote_address, default_limits=[os.getenv("RATE_LIMIT")])

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.get("/")
async def root():
  return {"message": "You should not be seeing this"}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app)