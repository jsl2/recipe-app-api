from django.core.management import call_command
from django.db.utils import OperationalError


def test_wait_for_db_ready(mocker):
    """Test waiting for db when db is available"""
    gi = mocker.patch("django.db.utils.ConnectionHandler.__getitem__")
    gi.return_value = True
    call_command("wait_for_db")
    assert gi.call_count == 1


def test_wait_for_db(mocker):
    """Test waiting for db"""
    mocker.patch("time.sleep", return_value=True)
    gi = mocker.patch("django.db.utils.ConnectionHandler.__getitem__")
    gi.side_effect = [OperationalError] * 5 + [True]
    call_command("wait_for_db")
    assert gi.call_count == 6
