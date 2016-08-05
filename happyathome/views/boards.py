from flask import current_app, Blueprint, render_template, request, session, url_for, redirect
from happyathome.forms import Pagination
from happyathome.models import Board, db

boards = Blueprint('boards', __name__)


@boards.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


@boards.route('/<board_id>', defaults={'page': 1})
@boards.route('/<board_id>/page/<int:page>')
def list(board_id, page):
    posts = Board.query.filter_by(board_id=board_id)
    pagination = Pagination(page, 10, posts.count())
    offset = (10 * (page - 1)) if page != 1 else 0
    posts = posts.order_by(Board.group_id.desc(), Board.depth.asc(), Board.sort.asc()).limit(10).offset(offset).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/boards/list.html',
                           board_id=board_id,
                           posts=posts,
                           pagination=pagination)


@boards.route('/<board_id>/new', methods=['POST'])
def new(board_id):
    if request.method == 'POST':
        post = Board()
        post.board_id = board_id
        post.group_id = post.max1_group_id
        post.user_id = session['user_id']
        post.content = request.form['board_content']
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('boards.list', board_id=board_id))


@boards.route('/<board_id>/delete/<id>')
def delete(board_id, id):
    post = Board.query.filter_by(user_id=session['user_id'], board_id=board_id, id=id)
    board = post.first()

    if not board.depth:
        group = Board.query.filter_by(group_id=board.group_id)
        group.delete()
    else:
        post.delete()

    db.session.commit()

    return redirect(url_for('boards.list', board_id=board_id))
