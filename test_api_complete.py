import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from main_complete import app
from database import Base, get_db
from models import User
from utils.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    return TestClient(app)

@pytest.fixture
def test_user(client):
    # Create a test user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login to get tokens
    login_response = client.post("/auth/login", json=user_data)
    assert login_response.status_code == 200
    tokens = login_response.json()
    
    return {
        "email": user_data["email"],
        "password": user_data["password"],
        "tokens": tokens
    }

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_register_user(client):
    """Test user registration"""
    user_data = {
        "email": "newuser@example.com",
        "password": "TestPassword123!"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "created_at" in data
    assert data["is_active"] == True

def test_register_duplicate_email(client, test_user):
    """Test duplicate email registration"""
    user_data = {
        "email": test_user["email"],
        "password": "AnotherPassword123!"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success(client, test_user):
    """Test successful login"""
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123!"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token"""
    response = client.get("/users/me")
    assert response.status_code == 403

def test_protected_endpoint_with_token(client, test_user):
    """Test accessing protected endpoint with valid token"""
    headers = {"Authorization": f"Bearer {test_user['tokens']['access_token']}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]

def test_create_project(client, test_user):
    """Test creating a project"""
    headers = {"Authorization": f"Bearer {test_user['tokens']['access_token']}"}
    project_data = {
        "name": "Test Project",
        "github_url": "https://github.com/user/test-project"
    }
    response = client.post("/projects", json=project_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == project_data["name"]
    assert data["github_url"] == project_data["github_url"]
    assert data["status"] == "active"
    assert "id" in data
    assert "user_id" in data

def test_list_projects(client, test_user):
    """Test listing user's projects"""
    headers = {"Authorization": f"Bearer {test_user['tokens']['access_token']}"}
    # Create a project first
    project_data = {
        "name": "Test Project",
        "github_url": "https://github.com/user/test-project"
    }
    client.post("/projects", json=project_data, headers=headers)
    
    # List projects
    response = client.get("/projects", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == project_data["name"]

def test_trigger_deployment(client, test_user):
    """Test triggering a deployment"""
    headers = {"Authorization": f"Bearer {test_user['tokens']['access_token']}"}
    # Create a project first
    project_data = {
        "name": "Test Project",
        "github_url": "https://github.com/user/test-project"
    }
    project_response = client.post("/projects", json=project_data, headers=headers)
    project_id = project_response.json()["id"]
    
    # Trigger deployment
    response = client.post(f"/projects/{project_id}/deploy", headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project_id
    assert data["status"] == "pending"
    assert "id" in data
    assert "started_at" in data

def test_get_deployment_logs(client, test_user):
    """Test getting deployment logs"""
    headers = {"Authorization": f"Bearer {test_user['tokens']['access_token']}"}
    # Create project and deployment
    project_data = {
        "name": "Test Project",
        "github_url": "https://github.com/user/test-project"
    }
    project_response = client.post("/projects", json=project_data, headers=headers)
    project_id = project_response.json()["id"]
    
    deployment_response = client.post(f"/projects/{project_id}/deploy", headers=headers)
    deployment_id = deployment_response.json()["id"]
    
    # Get logs
    response = client.get(f"/deployments/{deployment_id}/logs", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "Deployment queued" in data["logs"]

def test_refresh_token(client, test_user):
    """Test token refresh"""
    refresh_data = {
        "refresh_token": test_user["tokens"]["refresh_token"]
    }
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["refresh_token"] != test_user["tokens"]["refresh_token"]

def test_logout(client, test_user):
    """Test logout functionality"""
    refresh_data = {
        "refresh_token": test_user["tokens"]["refresh_token"]
    }
    headers = {"Authorization": f"Bearer {test_user['tokens']['access_token']}"}
    
    response = client.post("/auth/logout", json=refresh_data, headers=headers)
    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]

def test_rate_limiting(client):
    """Test rate limiting"""
    # Make multiple requests quickly
    for i in range(70):  # More than the 60 requests per minute limit
        response = client.get("/")
    
    # Should get rate limited
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

def test_health_endpoints_not_rate_limited(client):
    """Test that health endpoints are not rate limited"""
    # Make many requests to health endpoint
    for i in range(100):
        response = client.get("/health")
        assert response.status_code == 200  # Should not be rate limited

def test_admin_endpoints_require_admin(client, test_user):
    """Test admin endpoints require admin privileges"""
    headers = {"Authorization": f"Bearer {test_user['tokens']['access_token']}"}
    
    # Non-admin user should not access admin endpoints
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]

def test_detailed_health_check(client):
    """Test detailed health check endpoint"""
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "system" in data
    assert "services" in data
    assert "cpu_percent" in data["system"]
    assert "memory_percent" in data["system"]

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data

def test_info_endpoint(client):
    """Test info endpoint"""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "environment" in data
    assert "support" in data

def test_analytics_endpoints(client, test_user):
    """Test analytics endpoints"""
    headers = {"Authorization": f"Bearer {test_user['tokens']['access_token']}"}
    
    # Create a project first
    project_data = {
        "name": "Test Project",
        "github_url": "https://github.com/user/test-project"
    }
    project_response = client.post("/projects", json=project_data, headers=headers)
    project_id = project_response.json()["id"]
    
    # Test user analytics
    response = client.get("/analytics/user/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "period" in data
    
    # Test project analytics
    response = client.get(f"/analytics/project/{project_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "summary" in data

def test_cache_endpoints_require_admin(client, test_user):
    """Test cache endpoints require admin"""
    headers = {"Authorization": f"Bearer {test_user['tokens']['access_token']}"}
    
    # Non-admin user should not access cache endpoints
    response = client.get("/cache/stats", headers=headers)
    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
