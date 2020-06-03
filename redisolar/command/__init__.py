from flask import Blueprint
from .load import load

blueprint = Blueprint('students', __name__, cli_group=None)
blueprint.cli.command('load')(load)
