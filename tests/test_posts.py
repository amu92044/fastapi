from typing import List
from app import schemas
import pytest


def create_test_posts(client, test_user):
    # Create two test posts
    post_1 = {"title": "First Post", "content": "Content of first post", "published": True}
    post_2 = {"title": "Second Post", "content": "Content of second post", "published": False}

    headers = {"Authorization": f"Bearer {test_user['token']}"}

    client.post("/posts/", json=post_1, headers=headers)
    client.post("/posts/", json=post_2, headers=headers)

    # Get all posts
    res = client.get("/posts/", headers=headers)
    assert res.status_code == 200

    # Validate response structure
    posts: List[schemas.PostOut] = [schemas.PostOut(**p) for p in res.json()]
    assert len(posts) >= 2

    return posts


def test_unauthorized_user_get_all_posts(client):
    res = client.get("/posts/")  # Correct endpoint
    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"


def test_get_one_post_not_exists(client, test_user):
    res = client.get("/posts/9999", headers={"Authorization": f"Bearer {test_user['token']}"})
    assert res.status_code == 404


def test_get_all_posts(client, test_user):
    posts = create_test_posts(client, test_user)
    titles = [p.Post.title for p in posts]

    assert "First Post" in titles
    assert "Second Post" in titles

def test_get_one_post(client, test_user):
    posts = create_test_posts(client, test_user)
    post_id = posts[0].Post.id

    res = client.get(f"/posts/{post_id}", headers={"Authorization": f"Bearer {test_user['token']}"})
    assert res.status_code == 200
    

@pytest.mark.parametrize("title, content, published", [
    ("New Post 1", "Content 1", True),
])
def test_create_post(client, test_user, title, content, published):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    post_data = {"title": title, "content": content, "published": published}
    res = client.post("/posts/", json=post_data, headers=headers)

    assert res.status_code == 201

    post = res.json()["Post"]
    assert post["title"] == title
    assert post["content"] == content
    assert post["published"] == published

def test_create_post_default_published(client, test_user):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    post_data = {
        "title": "Post without published field",
        "content": "Some content"
    }

    res = client.post("/posts/", json=post_data, headers=headers)

    assert res.status_code == 201
    post = res.json()["Post"]
    assert post["title"] == post_data["title"]
    assert post["content"] == post_data["content"]
    assert post["published"] is True  # Assuming default=True

def test_unauthorized_user_delete_post(client):
    res = client.delete("/posts/1")  # Attempt to delete without auth
    assert res.status_code == 401
    assert res.json().get("detail") == "Not authenticated"
    
def test_delete_post_not_exists(client, test_user):
    res = client.delete("/posts/9999", headers={"Authorization": f"Bearer {test_user['token']}"})
    assert res.status_code == 404
    
def test_delete_post(client, test_user):
    posts = create_test_posts(client, test_user)
    post_id = posts[0].Post.id

    res = client.delete(f"/posts/{post_id}", headers={"Authorization": f"Bearer {test_user['token']}"})
    assert res.status_code == 204

    # Verify deletion
    get_res = client.get(f"/posts/{post_id}", headers={"Authorization": f"Bearer {test_user['token']}"})
    assert get_res.status_code == 404
    
def test_delete_other_user_post(client, test_user):
    # Step 1: Create a second user (the post owner)
    other_user_data = {
        "email": "otheruser@example.com",
        "password": "otherpassword"
    }

    # Register the second user
    res = client.post("/users/", json=other_user_data)
    assert res.status_code == 201 or res.status_code == 409  # in case user already exists

    # Step 2: Login with correct OAuth2 form fields
    login_data = {
        "username": other_user_data["email"],
        "password": other_user_data["password"]
    }

    login_res = client.post("/login", data=login_data)
    assert login_res.status_code == 200

    other_user_token = login_res.json()["access_token"]
    other_user_headers = {"Authorization": f"Bearer {other_user_token}"}

    # Step 3: Create a post with the other user
    post_data = {
        "title": "Other User's Post",
        "content": "This post belongs to another user",
        "published": True
    }

    post_res = client.post("/posts/", json=post_data, headers=other_user_headers)
    assert post_res.status_code == 201

    post_id = post_res.json()["Post"]["id"]

    # Step 4: Try deleting the post using the test_user's token
    test_user_headers = {"Authorization": f"Bearer {test_user['token']}"}
    delete_res = client.delete(f"/posts/{post_id}", headers=test_user_headers)

    # Step 5: Assert forbidden
    assert delete_res.status_code == 403


def test_update_post(client, test_user):
    posts = create_test_posts(client, test_user)
    post_id = posts[0].Post.id

    update_data = {
        "title": "Updated Title",
        "content": "Updated Content",
        "published": False
    }

    res = client.put(f"/posts/{post_id}", json=update_data, headers={"Authorization": f"Bearer {test_user['token']}"})
    assert res.status_code == 200

    updated_post = res.json()["Post"]
    assert updated_post["title"] == update_data["title"]
    assert updated_post["content"] == update_data["content"]
    assert updated_post["published"] == update_data["published"]
    
def test_update_other_user_post(client, test_user, test_user2):
    # Step 1: Login as test_user2 (the post owner)
    login_res = client.post("/login", data={
        "username": test_user2["email"],
        "password": test_user2["password"]
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Create a post as test_user2
    post_data = {
        "title": "Other User's Post",
        "content": "This post belongs to another user",
        "published": True
    }
    post_res = client.post("/posts/", json=post_data, headers=headers)
    assert post_res.status_code == 201
    post_id = post_res.json()["Post"]["id"]

    # Step 3: Try to update the post using test_user (not the owner)
    update_data = {
        "title": "Hacked Title",
        "content": "Hacked Content",
        "published": False
    }
    test_user_headers = {"Authorization": f"Bearer {test_user['token']}"}
    update_res = client.put(f"/posts/{post_id}", json=update_data, headers=test_user_headers)

    # Step 4: Assert forbidden
    assert update_res.status_code == 403
