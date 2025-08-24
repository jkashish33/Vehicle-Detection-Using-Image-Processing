from flask import Flask, send_from_directory
from flask_restx import Api
import os
from db_handler import DBHandler

db_handler = DBHandler()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db_handler.init_app(app)
    api = Api(app, version='1.0', title='Vehicle Detection API', doc='/')

    from routes.vehicle import api as vehicle_ns
    api.add_namespace(vehicle_ns, path='/vehicle')

    # Ensure processed directory exists
    processed_dir = os.path.join(os.path.dirname(__file__), 'processed')
    os.makedirs(processed_dir, exist_ok=True)

    @app.route('/vehicle/download/<filename>')
    def download_file(filename):
        """Download processed image or video by filename"""
        return send_from_directory(processed_dir, filename, as_attachment=True)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db_handler.create_all()
    app.run(debug=True)