from pydantic import BaseModel, Field

class AuthTokenResponse(BaseModel):
    access_token: str | None = Field(default=None, json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaGFuIjoiMjMwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"})
    refresh_token: str | None = Field(default=None, json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaGFuIjoiMjMwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"})
    token_type: str | None = Field(default=None, json_schema_extra={"example": "bearer"})

class TokenData(BaseModel):
    username: str | None = None
