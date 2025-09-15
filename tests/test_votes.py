import pytest
from app import models
@pytest.fixture()
def test_votes(client, test_user, test_posts):
    # User votes on the first post
    client.post(
        "/vote/",
        json={"post_id": test_posts[0].id, "dir": 1},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    return test_posts

def test_vote_on_post(test_posts, authorized_client, client, test_user):
    post_id = test_posts[0].id
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    vote_data = {"post_id": post_id, "dir": 1}

    res = client.post("/vote/", json=vote_data, headers=headers)
    assert res.status_code == 201
    assert res.json() == {"message": "successfully added vote"}
    
def test_vote_twice_on_post(test_posts, authorized_client, client, test_user):
    post_id = test_posts[0].id
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    vote_data = {"post_id": post_id, "dir": 1}

    # First vote should succeed
    res1 = client.post("/vote/", json=vote_data, headers=headers)
    assert res1.status_code == 201
    assert res1.json() == {"message": "successfully added vote"}

    # Second vote on the same post should fail
    res2 = client.post("/vote/", json=vote_data, headers=headers)
    assert res2.status_code == 409
    assert res2.json().get("detail") == f"user {test_user['id']} has already voted on post {post_id}"

def test_delete_vote(test_posts, authorized_client, client, test_user):
    post_id = test_posts[0].id
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    vote_data = {"post_id": post_id, "dir": 1}
    # First, add a vote
    client.post("/vote/", json=vote_data, headers=headers)
    # Now, delete the vote
    delete_data = {"post_id": post_id, "dir": 0}
    res = client.post("/vote/", json=delete_data, headers=headers)
    assert res.status_code == 201
    assert res.json() == {"message": "successfully deleted vote"}
    