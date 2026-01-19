from app.services.supabase import get_supabase_client
from app.services.ollama import get_ollama_client
from app.services.comfyui import get_comfyui_client


def get_db():
    return get_supabase_client()


def get_ollama():
    return get_ollama_client()


def get_comfyui():
    return get_comfyui_client()
