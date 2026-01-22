import os
import shutil
from fastapi.testclient import TestClient
from main import app, STORAGE_DIR, FileCounter

client = TestClient(app)


def setup_module(module):
    # Ensure clean storage before tests
    if STORAGE_DIR.exists():
        shutil.rmtree(STORAGE_DIR)
    STORAGE_DIR.mkdir()

    # Reset singleton counter
    FileCounter._instance = None


def teardown_module(module):
    # Cleanup storage after tests
    if STORAGE_DIR.exists():
        shutil.rmtree(STORAGE_DIR)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "File Storage API" in data["message"]


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_file_upload_and_list():
    file_content = b"hello world"
    response = client.post(
        "/files",
        files={"file": ("test.txt", file_content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["size"] == len(file_content)

    # List files
    response = client.get("/files")
    assert response.status_code == 200
    data = response.json()
    assert "test.txt" in data["files"]
    assert data["count"] == 1


def test_get_file():
    response = client.get("/files/test.txt")
    assert response.status_code == 200
    assert response.content == b"hello world"


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["files_current"] == 1
    assert data["files_stored_total"] == 1
    assert data["total_storage_bytes"] > 0
