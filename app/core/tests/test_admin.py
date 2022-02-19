import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

from core.models import User


@pytest.fixture()
def admin_user(db):
    return get_user_model().objects.create_superuser(
        email="admin@testing.com", password="test123"
    )


@pytest.fixture()
def user(db):
    return get_user_model().objects.create_user(
        email="user@testing.com", password="test123", name="Test user full name"
    )


@pytest.fixture()
def client(db, admin_user):
    client = Client()
    client.force_login(admin_user)
    return client


def test_users_listed(client: Client, user: User):
    """Test that users are listed on user page"""
    url = reverse("admin:core_user_changelist")
    res = client.get(url)

    assert user.name in res.content.decode("utf-8")
    assert user.email in res.content.decode("utf-8")


def test_user_change_page(client: Client, user: User):
    """Test that the user edit page works"""
    url = reverse("admin:core_user_change", args=[user.id])
    res = client.get(url)

    assert res.status_code == 200


def test_create_user_page(client: Client):
    """Test that the create user page works"""
    url = reverse("admin:core_user_add")
    res = client.get(url)

    assert res.status_code == 200
