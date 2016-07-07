from happyathome import create_app

app = create_app()

if __name__ == '__main__':
    from flask_script import Manager

    manager = Manager(app)
    manager.run()
