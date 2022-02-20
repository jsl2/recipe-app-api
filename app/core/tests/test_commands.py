from django.core.management import call_command
from django.db.utils import OperationalError


def test_wait_for_db_ready(mocker):
    """Test waiting for db when db is available"""
    ec = mocker.patch(
        "django.db.backends.base.base.BaseDatabaseWrapper.ensure_connection",
        return_value=None,
    )
    call_command("wait_for_db")
    assert ec.call_count == 1


def test_wait_for_db(mocker):
    """Test waiting for db"""
    mocker.patch("time.sleep", return_value=True)
    ec = mocker.patch(
        "django.db.backends.base.base.BaseDatabaseWrapper.ensure_connection",
        return_value=None,
    )
    ec.side_effect = [OperationalError] * 5 + [True]
    call_command("wait_for_db")
    assert ec.call_count == 6
