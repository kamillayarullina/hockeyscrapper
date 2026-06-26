import pytest
from fastapi.testclient import TestClient
from Backend.main import app

def test_qrt_02_unauthorized_access_rejection():
    """
    QRT-02 (Security - Confidentiality):
    Ensures that a request to secure, authenticated endpoints without valid JWT Bearer credentials 
    is immediately rejected with a 401 status code.
    """
    client = TestClient(app)
    
    # Dynamically define a mock protected endpoint under app to test Dependency injection
    @app.get("/api/v1/test-quality-gate-confidentiality")
    def secure_route(current_user: dict = pytest.importorskip("fastapi").Depends(pytest.importorskip("Backend.jwt_auth").get_current_user)):
        return {"status": "success"}

    # Attempt request with NO token headers
    response = client.get("/api/v1/test-quality-gate-confidentiality")
    
    # Verify that the gateway blocks the request strictly with 401
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"