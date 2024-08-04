from __future__ import annotations

from application import create_app
from application import db


app = create_app()

with app.app_context():
    from application.routes import invoice
    app.register_blueprint(invoice)
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
