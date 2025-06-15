import pytest
from unittest.mock import patch, MagicMock
from app import app

def test_home():
    """Test that the home page loads successfully."""
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        assert b"PipeGuard" in response.data

@patch('app.firestore.Client')
def test_home_with_mock_firestore(mock_firestore):
    """Test home page with mocked Firestore to avoid connection issues."""
    # Mock the Firestore client and its methods
    mock_db = MagicMock()
    mock_firestore.return_value = mock_db
    
    # Mock collection queries
    mock_runs_collection = MagicMock()
    mock_anomalies_collection = MagicMock()
    
    mock_db.collection.side_effect = lambda name: {
        'runs': mock_runs_collection,
        'anomalies': mock_anomalies_collection
    }[name]
    
    # Mock query results
    mock_runs_collection.order_by.return_value.limit.return_value.get.return_value = []
    mock_anomalies_collection.order_by.return_value.limit.return_value.get.return_value = []
    
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        assert b"PipeGuard" in response.data
