"""
gunicorn 실행 모듈

/var/app/inotone/bin/gunicorn manage:app -w 3
"""
import os

from flask import request
from happyathome import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.url_defaults
def hashed_url_for_static_file(endpoint, values):
    if 'static' == endpoint or endpoint.endswith('.static'):
        filename = values.get('filename')
        if filename:
            if '.' in endpoint:  # has higher priority
                blueprint = endpoint.rsplit('.', 1)[0]
            else:
                blueprint = request.blueprint  # can be None too

            if blueprint:
                static_folder = app.blueprints[blueprint].static_folder or app.static_folder
            else:
                static_folder = app.static_folder

            param_name = 'q'
            while param_name in values:
                param_name = '_' + param_name
            values[param_name] = static_file_hash(os.path.join(static_folder, filename))


def static_file_hash(filename):
    return int(os.stat(filename).st_mtime)


if __name__ == '__main__':
    from flask_script import Manager

    manager = Manager(app)
    manager.run()
