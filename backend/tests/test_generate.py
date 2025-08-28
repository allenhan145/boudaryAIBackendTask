import pytest


@pytest.mark.asyncio
async def test_generate_new_survey_returns_201_and_json(client):
    resp = await client.post(
        "/api/surveys/generate", json={"description": "customer feedback"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"]
    assert len(data["questions"]) >= 1


@pytest.mark.asyncio
async def test_invalid_input_400(client):
    resp = await client.post("/api/surveys/generate", json={"description": "bad"})
    assert resp.status_code == 400
