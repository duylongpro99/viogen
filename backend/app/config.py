from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = "http://localhost:54321"
    supabase_key: str = "your-anon-key"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # ComfyUI
    comfyui_base_url: str = "http://localhost:8188"

    # App
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
