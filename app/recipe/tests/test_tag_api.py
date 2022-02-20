import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, User

from recipe.serializers import TagSerializer

TAGS_URLS = reverse("recipe:tag-list")


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


def test_login_required(api_client):
    """Test that login is required for retrieving tags"""
    res = api_client.get(TAGS_URLS)

    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_retrieve_tags(authenticated_user: User, api_client: APIClient):
    """Test retrieving tags"""
    Tag.objects.create(user=authenticated_user, name="Vegan")
    Tag.objects.create(user=authenticated_user, name="Dessert")

    res = api_client.get(TAGS_URLS)
    tags = Tag.objects.all().order_by("-name")
    serializer = TagSerializer(tags, many=True)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == serializer.data


def test_tags_limited_to_user(authenticated_user: User, api_client: APIClient):
    """Test that tags returned are for the authenticated user"""
    user2 = create_user(email="other@testing.com", password="testpass")
    Tag.objects.create(user=user2, name="Fruity")
    tag = Tag.objects.create(user=authenticated_user, name="Comfort Food")

    res = api_client.get(TAGS_URLS)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 1
    assert res.data[0]["name"] == tag.name
