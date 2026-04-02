from flask import Flask
from config import Config
from models import db
from routes import register_routes
from flasgger import Swagger

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

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True, port=8081)
