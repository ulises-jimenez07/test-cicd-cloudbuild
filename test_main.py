import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient  # Import TestClient
from main import app, big_query_client as app_client  # Correct client import


@pytest.fixture
def client():
    with TestClient(app) as client:  # Use TestClient properly
        yield client


@patch.object(app_client, "load_table_from_uri")
@patch.object(app_client, "get_table")
def test_main_endpoint(mock_get_table, mock_load_table_from_uri, client):
    expected_rows = 50  # Use a variable for expected rows

    mock_load_job = MagicMock()
    mock_load_table_from_uri.return_value = mock_load_job

    mock_table = MagicMock()
    mock_table.num_rows = expected_rows
    mock_get_table.return_value = mock_table

    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"] == expected_rows  # Correct assertion

    mock_load_table_from_uri.assert_called_once()
    mock_load_job.result.assert_called_once()
    mock_get_table.assert_called_once()
