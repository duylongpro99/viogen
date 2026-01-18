import pytest


def test_supabase_client_connects(supabase_client):
    # Should be able to query sessions table
    result = supabase_client.table("sessions").select("*").limit(1).execute()
    assert result.data is not None
