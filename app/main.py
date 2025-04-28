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

from app.routes import InstitutionType, User, Institution, Ppda, Auth, UserInstitution, Report, DeadLine, History, ActionType, Action
from app.routes import InstitutionType, User, Institution, Ppda, Auth, UserInstitution, Report, DeadLine, History, Kpi, Variable, ActionType, Action
from app.utils.docs import tags_metadata
from app.db import init_db

load_dotenv()
init_db()

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

app = FastAPI(
  middleware=middleware,
  openapi_tags=tags_metadata
)

app.include_router(User.router)
app.include_router(InstitutionType.router)
app.include_router(Institution.router)
app.include_router(Ppda.router)
app.include_router(Auth.router)
app.include_router(UserInstitution.router)
app.include_router(Report.router)
app.include_router(DeadLine.router)
app.include_router(History.router)
app.include_router(Kpi.router)
app.include_router(Variable.router)
app.include_router(ActionType.router)
app.include_router(Action.router)


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