import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import User


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    params["password"] = make_password(params["password"])
    return get_user_model().objects.create(**params)


@pytest.fixture()
def api_client(db):
    return APIClient()


@pytest.fixture()
def authenticated_user(api_client: APIClient):
    user = create_user(email="test@testing.com", password="testpass", name="name")
    api_client.force_authenticate(user=user)
    return user


def test_create_valid_user_success(api_client: APIClient):
    """Test creating user with valid payload is successful"""
    payload = {"email": "test@testing.com", "password": "testpass", "name": "Test name"}
    res = api_client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_201_CREATED
    user = get_user_model().objects.get(**res.data)
    assert user.check_password(payload["password"])
    assert "password" not in res.data


def test_user_exists(api_client: APIClient):
    """Test creating a user that already exists fails"""
    payload = {"email": "test@testing.com", "password": "testpass", "name": "Test name"}
    create_user(**payload)
    res = api_client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_password_too_short(api_client: APIClient):
    """Test that the password must be more than 5 characters"""
    payload = {"email": "test@testing.com", "password": "pw", "name": "Test name"}
    res = api_client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_400_BAD_REQUEST
    user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
    assert not user_exists


def test_create_token_for_user(api_client: APIClient):
    """Test that a token is created for the user"""
    payload = {"email": "test@testing.com", "password": "testpass", "name": "Test name"}
    create_user(**payload)
    res = api_client.post(TOKEN_URL, payload)

    assert "token" in res.data
    assert res.status_code == status.HTTP_200_OK


def test_create_token_invalid_credentials(api_client: APIClient):
    """Test that token is not created if invalid credentials are given"""
    create_user(email="test@testing.com", password="testpass", name="Test")
    payload = {"email": "test@testing.com", "password": "wrong"}
    res = api_client.post(TOKEN_URL, payload)

    assert "token" not in res.data
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_create_token_no_user(api_client: APIClient):
    """Test that token is not created if user doesn't exist"""
    payload = {"email": "test@testing.com", "password": "testpass", "name": "Test name"}
    res = api_client.post(TOKEN_URL, payload)

    assert "token" not in res.data
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_create_token_missing_password(api_client: APIClient):
    """Test that missing password raises error"""
    res = api_client.post(TOKEN_URL, {"email": "test@testing.com", "password": ""})
    assert "token" not in res.data
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_retrieve_user_unauthorized(api_client: APIClient):
    """Test that authentication is required for users"""
    res = api_client.get(ME_URL)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_retrieve_profile_success(api_client: APIClient, authenticated_user: User):
    """Test retrieving profile for logged in user"""
    res = api_client.get(ME_URL)

    assert res.status_code == status.HTTP_200_OK
    assert res.data == {
        "name": authenticated_user.name,
        "email": authenticated_user.email,
    }


def test_post_me_not_allowed(api_client: APIClient, authenticated_user: User):
    """Test that POST is not allowed on the me url"""
    res = api_client.post(ME_URL, {})

    assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_update_user_profile(api_client: APIClient, authenticated_user: User):
    """Test updating the user profile for the authenticated user"""
    payload = {"name": "new name", "password": "newpassword123"}
    res = api_client.patch(ME_URL, payload)
    authenticated_user.refresh_from_db()
    assert authenticated_user.name == payload["name"]
    assert authenticated_user.check_password(payload["password"])
    assert res.status_code == status.HTTP_200_OK
