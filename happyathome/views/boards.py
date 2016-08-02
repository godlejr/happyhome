from flask import Blueprint
from flask import current_app
from flask import render_template
from happyathome.forms import Pagination
from happyathome.models import Board

boards = Blueprint('boards', __name__)


@boards.route('/<board_id>', defaults={'page': 1})
@boards.route('/<board_id>/page/<int:page>')
def list(board_id, page):
    posts = Board.query.filter_by(board_id=board_id)
    pagination = Pagination(page, 10, posts.count())
    offset = (10 * (page - 1)) if page != 1 else 0
    posts = posts.order_by(Board.id.desc()).limit(10).offset(offset).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/boards/list.html',
                           posts=posts,
                           pagination=pagination)
