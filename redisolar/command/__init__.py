from flask import Blueprint
from .load import load

blueprint = Blueprint('students', __name__, cli_group=None)  # type:ignore
blueprint.cli.command('load')(load)  # type: ignore
