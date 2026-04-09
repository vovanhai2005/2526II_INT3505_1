#!/usr/bin/env python3

import os
import connexion
from dotenv import load_dotenv

from swagger_server import encoder
from swagger_server.database import mongo

# Load environment variables from swagger_server/.env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        app.app.json_encoder = encoder.JSONEncoder

    # Setup MongoDB
    app.app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/libraryBuoi7")
    mongo.init_app(app.app)

    with app.app.app_context():
        try:
            mongo.db.command('ping')
            print("=======================================")
            print("SUCCESS: Connected to MongoDB database!")
            print("=======================================")
        except Exception as e:
            print("=======================================")
            print(f"ERROR: Failed to connect to MongoDB! {e}")
            print("=======================================")

    app.add_api('swagger.yaml', arguments={'title': 'Library Management API (Buoi7)'}, pythonic_params=True)
    app.run(port=8080)

if __name__ == '__main__':
    main()
