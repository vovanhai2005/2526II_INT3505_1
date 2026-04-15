from flask import Flask
from flasgger import Swagger

from config import Config
from models import db
from routes import apply_routes

app = Flask(__name__)
app.config.from_object(Config)
app.config['SWAGGER'] = {
    'openapi': '3.0.3',
    'uiversion': 3
}

db.init_app(app)

swagger = Swagger(app, template_file="swagger.yml")

with app.app_context():
    db.create_all()

apply_routes(app)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
