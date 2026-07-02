from fastapi.testclient import TestClient
from Backend.main import app

def test_qrt_02_unauthorized_access_rejection():
    """
    QRT-02 (Security - Confidentiality):
    Ensures that a request to secure, authenticated endpoints without valid JWT Bearer credentials 
    is immediately rejected with a 401 status code.
    """
    client = TestClient(app)

    # Attempt request with NO token headers to a known protected endpoint like /me.
    # Dynamically adding routes inside a test can lead to inconsistent behavior with TestClient.
    response = client.get("/me")
    
    # Verify that the gateway blocks the request strictly with 401
    assert response.status_code == 401