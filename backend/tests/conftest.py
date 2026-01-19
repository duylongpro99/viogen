import pytest
from app.config import settings


@pytest.fixture
def supabase_client():
    from app.services.supabase import get_supabase_client
    return get_supabase_client()
