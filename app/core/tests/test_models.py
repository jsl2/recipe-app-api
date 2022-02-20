import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from core import models


def sample_user(email="test@testing.com", password="testpass"):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, make_password(password))


@pytest.mark.django_db(True)
def test_create_user_with_email_successful():
    """Test creating a new user with an email is successful"""
    email = "test@testing.com"
    password = "Testpass123"
    user = get_user_model().objects.create_user(email=email, password=password)

    assert user.email == email
    assert user.check_password(password)


@pytest.mark.django_db(True)
def test_new_user_email_normalized():
    """Test the email for a new user is normalized"""
    email = "test@TESTING.COM"
    user = get_user_model().objects.create_user(email, "test123")

    assert user.email == email.lower()


@pytest.mark.django_db(True)
def test_new_user_invalid_email():
    """Test creating user with no email raises error"""
    with pytest.raises(ValueError):
        get_user_model().objects.create_user("", "test123")


@pytest.mark.django_db(True)
def test_create_new_superuser():
    """Test creating a new superuser"""
    user = get_user_model().objects.create_superuser("test@testing.com", "test123")

    assert user.is_superuser
    assert user.is_staff


@pytest.mark.django_db(True)
def test_tag_str():
    """Test the tag string representation"""
    tag = models.Tag.objects.create(user=sample_user(), name="Vegan")

    assert str(tag) == tag.name
