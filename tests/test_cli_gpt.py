import sys
import os
import pytest
import click
from unittest.mock import MagicMock, patch
from pathlib import Path
from click.testing import CliRunner
from flask import Flask, Blueprint
from flask.cli import find_best_app, NoAppException, run_command

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

cwd = Path.cwd()
test_path = (Path(__file__) / ".." / "test_apps").resolve()

@pytest.fixture
def runner():
    return CliRunner()

def test_find_best_app():
    class Module:
        app = Flask("appname")
    assert find_best_app(Module) == Module.app

    class Module:
        application = Flask("appname")
    assert find_best_app(Module) == Module.application

    class Module:
        myapp = Flask("appname")
    assert find_best_app(Module) == Module.myapp

    class Module:
        @staticmethod
        def create_app():
            return Flask("appname")
    app = find_best_app(Module)
    assert isinstance(app, Flask)
    assert app.name == "appname"

    class Module:
        @staticmethod
        def create_app(**kwargs):
            return Flask("appname")
    app = find_best_app(Module)
    assert isinstance(app, Flask)
    assert app.name == "appname"

    class Module:
        @staticmethod
        def make_app():
            return Flask("appname")
    app = find_best_app(Module)
    assert isinstance(app, Flask)
    assert app.name == "appname"

    class Module:
        myapp = Flask("appname1")
        @staticmethod
        def create_app():
            return Flask("appname2")
    assert find_best_app(Module) == Module.myapp

    class Module:
        myapp = Flask("appname1")
        @staticmethod
        def create_app():
            return Flask("appname2")
    assert find_best_app(Module) == Module.myapp

    class Module:
        pass
    pytest.raises(NoAppException, find_best_app, Module)

    class Module:
        myapp1 = Flask("appname1")
        myapp2 = Flask("appname2")
    pytest.raises(NoAppException, find_best_app, Module)

def test_run_cert_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "ssl", None)

    with pytest.raises(click.BadParameter):
        run_command.make_context("run", ["--cert", "not_here"])

def test_cli_blueprints(app):
    custom = Blueprint("custom", __name__, cli_group="customized")
    nested = Blueprint("nested", __name__)
    merged = Blueprint("merged", __name__, cli_group=None)
    late = Blueprint("late", __name__)

    @custom.cli.command("custom")
    def custom_command():
        click.echo("custom_result")

    @nested.cli.command("nested")
    def nested_command():
        click.echo("nested_result")

    @merged.cli.command("merged")
    def merged_command():
        click.echo("merged_result")

    @late.cli.command("late")
    def late_command():
        click.echo("late_result")

    app.register_blueprint(custom)
    app.register_blueprint(nested)
    app.register_blueprint(merged)
    app.register_blueprint(late, cli_group="late_registration")

    app_runner = app.test_cli_runner()

    result = app_runner.invoke(args=["customized", "custom"])
    assert "custom_result" in result.output

    result = app_runner.invoke(args=["nested", "nested"])
    assert "nested_result" in result.output

    result = app_runner.invoke(args=["merged"])
    assert "merged_result" in result.output

    result = app_runner.invoke(args=["late_registration", "late"])
    assert "late_result" in result.output

def test_cli_empty(app):
    bp = Blueprint("blue", __name__, cli_group="blue")
    app.register_blueprint(bp)

    result = app.test_cli_runner().invoke(args=["blue", "--help"])
    assert result.exit_code == 2, f"Unexpected success:\n\n{result.output}"

def test_run_exclude_patterns():
    ctx = run_command.make_context("run", ["--exclude-patterns", __file__])
    assert ctx.params["exclude_patterns"] == [__file__]

# ----------------------------------------------------------------------------

from flask.cli import _called_with_wrong_args

def function_with_args(a, b):
    return a + b

def function_with_error():
    return 1 / 0

def test_called_with_wrong_args_type_error():
    try:
        function_with_args(1)  # This will raise a TypeError
    except TypeError:
        assert _called_with_wrong_args(function_with_args) == True

def test_called_with_wrong_args_zero_division_error():
    try:
        function_with_error()  # This will raise a ZeroDivisionError
    except ZeroDivisionError:
        assert _called_with_wrong_args(function_with_error) == False

# ----------------------------------------------------------------------------

import pytest
from types import ModuleType
from click.testing import CliRunner
from flask.cli import find_best_app, find_app_by_string, NoAppException
from flask import Flask

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_name(test_apps):
    """Make sure the CLI object's name is the app's name and not the app itself"""
    from cliapp.app import testapp
    assert testapp.cli.name == testapp.name

def test_find_best_app(test_apps):
    class Module:
        app = Flask("appname")
    assert find_best_app(Module) == Module.app

    class Module:
        application = Flask("appname")
    assert find_best_app(Module) == Module.application

    class Module:
        myapp = Flask("appname")
    assert find_best_app(Module) == Module.myapp

    class Module:
        @staticmethod
        def create_app():
            return Flask("appname")
    app = find_best_app(Module)
    assert isinstance(app, Flask)
    assert app.name == "appname"

    class Module:
        @staticmethod
        def create_app(**kwargs):
            return Flask("appname")
    app = find_best_app(Module)
    assert isinstance(app, Flask)
    assert app.name == "appname"

    class Module:
        @staticmethod
        def make_app():
            return Flask("appname")
    app = find_best_app(Module)
    assert isinstance(app, Flask)
    assert app.name == "appname"

    class Module:
        myapp = Flask("appname1")
        @staticmethod
        def create_app():
            return Flask("appname2")
    assert find_best_app(Module) == Module.myapp

    class Module:
        myapp = Flask("appname1")
        @staticmethod
        def create_app():
            return Flask("appname2")
    assert find_best_app(Module) == Module.myapp

    class Module:
        pass
    pytest.raises(NoAppException, find_best_app, Module)

    class Module:
        myapp1 = Flask("appname1")
        myapp2 = Flask("appname2")
    pytest.raises(NoAppException, find_best_app, Module)

# Adding tests for `find_app_by_string`
def test_find_app_by_string_variable():
    app = Flask(__name__)
    module = ModuleType('dummy_module')
    module.my_app = app

    result = find_app_by_string(module, 'my_app')
    assert result == app

def test_find_app_by_string_function():
    def create_app():
        return Flask(__name__)

    module = ModuleType('dummy_module')
    module.create_app = create_app
    result = find_app_by_string(module, 'create_app')
    assert isinstance(result, Flask)

def test_find_app_by_string_function_with_args():
    def create_app(arg1, arg2):
        assert arg1 == 'arg1'
        assert arg2 == 'arg2'
        return Flask(__name__)

    module = ModuleType('dummy_module')
    module.create_app = create_app
    result = find_app_by_string(module, 'create_app("arg1", "arg2")')
    assert isinstance(result, Flask)

def test_find_app_by_string_invalid_syntax():
    module = ModuleType('dummy_module')
    with pytest.raises(NoAppException, match="Failed to parse"):
        find_app_by_string(module, 'invalid_syntax(')

def test_find_app_by_string_no_such_attribute():
    module = ModuleType('dummy_module')
    with pytest.raises(NoAppException, match="Failed to find attribute"):
        find_app_by_string(module, 'non_existent')

def test_find_app_by_string_invalid_factory():
    def create_app(arg1):
        return Flask(__name__)

    module = ModuleType('dummy_module')
    module.create_app = create_app
    with pytest.raises(NoAppException, match="could not be called with the specified arguments"):
        find_app_by_string(module, 'create_app()')

def test_find_app_by_string_not_flask_instance():
    class NotFlask:
        pass

    module = ModuleType('dummy_module')
    module.my_app = NotFlask()
    with pytest.raises(NoAppException, match="A valid Flask application was not obtained"):
        find_app_by_string(module, 'my_app')

