# attempting to write tests for cli.py

import pytest
from unittest.mock import patch

from cli import find_best_app, NoAppException
from . import Flask

def test_find_best_app_with_app_variable():
    """Test finding the Flask app when it's assigned to the 'app' variable."""
    with patch("cli.Flask") as mock_flask:
        mock_app = mock_flask.return_value
        mock_module = types.ModuleType("test_module")
        mock_module.app = mock_app

        app = find_best_app(mock_module)
        assert app == mock_app

def test_find_best_app_with_application_variable():
    """Test finding the Flask app when it's assigned to the 'application' variable."""
    with patch("cli.Flask") as mock_flask:
        mock_app = mock_flask.return_value
        mock_module = types.ModuleType("test_module")
        mock_module.application = mock_app

        app = find_best_app(mock_module)
        assert app == mock_app

def test_find_best_app_with_single_instance():
    """Test finding the Flask app when there's only one instance in the module."""
    with patch("cli.Flask") as mock_flask:
        mock_app = mock_flask.return_value
        mock_module = types.ModuleType("test_module")
        mock_module.__dict__["app"] = mock_app  # Assign directly to __dict__

        app = find_best_app(mock_module)
        assert app == mock_app

def test_find_best_app_with_multiple_instances():
    """Test raising an exception when multiple Flask instances are found."""
    with patch("cli.Flask") as mock_flask:
        mock_app1 = mock_flask.return_value
        mock_app2 = mock_flask.return_value
        mock_module = types.ModuleType("test_module")
        mock_module.app1 = mock_app1
        mock_module.app2 = mock_app2

        with pytest.raises(NoAppException, match="Detected multiple Flask applications"):
            find_best_app(mock_module)

def test_find_best_app_with_create_app_factory():
    """Test finding the Flask app when using a 'create_app' factory function."""
    with patch("cli.Flask") as mock_flask:
        mock_app = mock_flask.return_value
        mock_module = types.ModuleType("test_module")

        def create_app():
            return mock_app

        mock_module.create_app = create_app

        app = find_best_app(mock_module)
        assert app == mock_app

def test_find_best_app_with_make_app_factory():
    """Test finding the Flask app when using a 'make_app' factory function."""
    with patch("cli.Flask") as mock_flask:
        mock_app = mock_flask.return_value
        mock_module = types.ModuleType("test_module")

        def make_app():
            return mock_app

        mock_module.make_app = make_app

        app = find_best_app(mock_module)
        assert app == mock_app

def test_find_best_app_with_failing_factory():
    """Test raising an exception when a factory function fails."""
    mock_module = types.ModuleType("test_module")

    def create_app():
        raise TypeError("Factory failure")

    mock_module.create_app = create_app

    with pytest.raises(NoAppException, match="could not call it without arguments"):
        find_best_app(mock_module)

def test_find_best_app_with_no_app():
    """Test raising an exception when no Flask app or factory is found."""
    mock_module = types.ModuleType("test_module")

    with pytest.raises(NoAppException, match="Failed to find Flask application or factory"):
        find_best_app(mock_module)
