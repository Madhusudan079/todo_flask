import pytest
from app import app

# Fixture for setting up test client
@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'supersecretkey'
    with app.test_client() as client:
        yield client

def test_login_and_access_todos(test_client): 
    # Simulate login
    login_data = {"email": "madhusudan07.code@gmail.com", "password": "Sourav$123"}
    login_response = test_client.post('/login', data=login_data)
    assert login_response.status_code == 302  # Should redirect to /todos after login

    # Access /todos after login
    todos_response = test_client.get('/todos', follow_redirects=True)
    assert todos_response.status_code == 200
    # assert b"Welcome to your Todos page!" in todos_response.data

    logout_response = test_client.get('/logout', follow_redirects=True)
    assert logout_response.status_code == 200

    login_response = test_client.post('/login', data=login_data)
    assert login_response.status_code == 302

    todos_response = test_client.get('/todos', follow_redirects=True)
    assert todos_response.status_code == 200