from __future__ import annotations

from application import create_app
from application import db
from flask_migrate import Migrate
from flask_script import Manager


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
