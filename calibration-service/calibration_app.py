from flask import Flask
from common_packages.models.models import db
from calibration import calibration_routes
import os

app = Flask(__name__)

app.register_blueprint(calibration_routes)


if os.getenv('TESTING', 'false').lower() == 'true':
    # For local testing with PostgreSQL container
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://calibration_user:calibration_pass@localhost:5432/calibration_db'
else:
    # For Docker deployment
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://calibration_user:calibration_pass@postgres:5432/calibration_db'
db.init_app(app)

# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
