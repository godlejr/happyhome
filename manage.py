import os

from flask_admin import Admin
from happyathome import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
admin = Admin(app, name='microblog', template_mode='bootstrap3')

if __name__ == '__main__':
    from flask_script import Manager

    manager = Manager(app)
    manager.run()
