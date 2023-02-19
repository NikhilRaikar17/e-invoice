from flask_script import Manager
from flask_migrate import Migrate
from application import create_app, db


app = create_app()

with app.app_context():
    from application.routes import invoice
    app.register_blueprint(invoice)
    db.create_all()


migrate = Migrate(app, db)
manager = Manager(app)

# manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
else:
    gunicorn_app = app
