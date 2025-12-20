from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "chainproof-ai-shield"
    cors_allow_origins: list[str] = ["*"]


settings = Settings()
