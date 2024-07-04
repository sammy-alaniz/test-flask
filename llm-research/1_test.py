import pytest
from datetime import timedelta
from flask import Flask

# Test fixtures
@pytest.fixture
def app():
    app = Flask(__name__)
    return app

@pytest.fixture
def app_context(app):
    with app.app_context():
        yield

# Tests for get_send_file_max_age
def test_get_send_file_max_age_default_none(app, app_context):
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = None
    assert app.get_send_file_max_age('somefile.txt') is None

def test_get_send_file_max_age_default_int(app, app_context):
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600
    assert app.get_send_file_max_age('somefile.txt') == 3600

def test_get_send_file_max_age_default_timedelta(app, app_context):
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(hours=1)
    assert app.get_send_file_max_age('somefile.txt') == 3600

