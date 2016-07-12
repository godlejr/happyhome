import os

from happyathome import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    from flask_script import Manager

    manager = Manager(app)
    manager.run()
