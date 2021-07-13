import pytest
from yaml import load
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"]  = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def header(client):
    user = client.post('/api/login', json=dict(
        username='testm',
        password= 'test2'
        # username='qixin',
        # password= 'qixin123'
        # username='qixin2',
        # password= 'qixin123'
    ))
    return {"Authorization": "Bosi "+user.get_json()["data"]["token"]}

with open("tests/args.yaml", encoding='utf8') as f:
    argsdata = load(f.read())
@pytest.fixture
def args():
    return argsdata