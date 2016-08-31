from flask import current_app, Blueprint, render_template, request, session, url_for, redirect
from flask_login import login_required, current_user
from happyathome.forms import Pagination
from happyathome.models import db, Board, User, BoardCategory

boards = Blueprint('boards', __name__)


@boards.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


@boards.route('/<id>', defaults={'page': 1})
@boards.route('/<id>/page/<int:page>')
def list(id, page):
    board_categories = BoardCategory.query.all()
    posts = Board.query.filter_by(board_id=id)
    category_id = request.args.get('category_id')
    if category_id:
        posts = posts.filter_by(category_id=category_id)
    pagination = Pagination(page, 10, posts.count())
    offset = (10 * (page - 1)) if page != 1 else 0
    posts = posts.order_by(Board.group_id.desc(), Board.depth.asc(), Board.sort.asc()).limit(10).offset(offset).all()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/boards/list.html',
                           board_id=id,
                           posts=posts,
                           board_categories=board_categories,
                           pagination=pagination,
                           query_string=request.query_string.decode('utf-8'))


@boards.route('/<board_id>/new', methods=['GET', 'POST'])
@login_required
def new(board_id):
    if request.method == 'POST':
        post = Board()
        post.user_id = current_user.id
        post.board_id = board_id
        post.group_id = post.max1_group_id
        post.category_id = request.form['board_category']
        post.title = request.form['board_title']
        post.content = request.form['board_content']
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('boards.list', id=board_id))


@boards.route('/<board_id>/<post_id>/reply', methods=['POST'])
@login_required
def reply(board_id, post_id):
    user = User.query.filter_by(id=current_user.id).first()
    if not user.is_pro and not user.is_admin:
        return redirect(url_for('boards.list', id=board_id))

    board = Board.query.filter_by(id=post_id).first()
    if request.method == 'POST':
        post = Board()
        post.user_id = user.id
        post.board_id = board.board_id
        post.group_id = board.group_id
        post.depth = board.max1_depth
        post.category_id = board.category_id
        post.title = 'Re: %s' % board.title
        post.content = request.form['reply_content']
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('boards.list', id=board_id))


@boards.route('/<board_id>/<post_id>/delete')
@login_required
def delete(board_id, post_id):
    post = Board.query.filter_by(board_id=board_id, id=post_id)
    board = post.first()

    if board.user_id != current_user.id:
        return redirect(url_for('boards.list', id=board_id))

    if board and board.is_reply:
        post.delete()
    else:
        group = Board.query.filter_by(board_id=board_id, group_id=board.group_id)
        group.delete()

    db.session.commit()

    return redirect(url_for('boards.list', id=board_id))
