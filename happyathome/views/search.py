from flask import Blueprint, current_app,render_template
from happyathome.models import Photo, Magazine

search = Blueprint('search', __name__)


@search.context_processor
def utility_processor():
    def url_for_s3(s3path, filename=''):
        return ''.join((current_app.config['S3_BUCKET_NAME'], current_app.config[s3path], filename))
    return dict(url_for_s3=url_for_s3)


@search.route('/search=<search>')
def list(search):
    photo = Photo.query.filter(Photo.content.like("%" + search + "%"))
    photo_count = photo.count()
    photos = photo.all()

    magazine = Magazine.query.filter(Magazine.title.like("%" + search + "%")).filter(
        Magazine.content.like("%" + search + "%"))
    magazine_count = magazine.count()
    magazines = magazine.all()

    return render_template(current_app.config['TEMPLATE_THEME'] + '/search/list.html', photos=photos,
                           magazines=magazines, photo_count=photo_count, magazine_count=magazine_count)
