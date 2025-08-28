import pytest


@pytest.mark.asyncio
async def test_generate_same_description_returns_cached_200(client):
    payload = {"description": "employee engagement"}
    first = await client.post("/api/surveys/generate", json=payload)
    assert first.status_code == 201
    survey_id = first.json()["id"]

    second = await client.post("/api/surveys/generate", json=payload)
    assert second.status_code == 200
    assert second.headers["X-Cache-Hit"] == "1"
    assert second.json()["id"] == survey_id
