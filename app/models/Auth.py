from pydantic import BaseModel

class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None

class TokenData(BaseModel):
    username: str | None = None
