from flask import Blueprint

main = Blueprint('main', __name__)

from alphahome.main import views
