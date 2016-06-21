from flask import Blueprint

snapshot = Blueprint('snapshot', __name__)

from alphahome.snapshot import views
