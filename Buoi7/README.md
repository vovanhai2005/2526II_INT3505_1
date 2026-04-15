# Library Management API (Buoi 7)

This project demonstrates an **API-first development workflow** using `openapi.yaml`, `swagger-codegen`, `Flask`, and `MongoDB`.

Follow the step-by-step guide below to recreate this project and resolve common code-generation issues.

---

## 1. Design the API (OpenAPI Specification)
Start by defining the API endpoints, schemas, and models in a file called `openapi.yaml` at the root of the project. This serves as the single source of truth for your API contract.

---

## 2. Download Swagger Codegen
Download the official Swagger Codegen CLI (`v3.0.52`) which reads the `openapi.yaml` and auto-generates the Python Flask server scaffolding.

```bash
curl https://repo1.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.52/swagger-codegen-cli-3.0.52.jar \
  -o swagger-codegen-cli.jar
```

---

## 3. Generate the Flask Server Scaffold
Run the Java tool against your `openapi.yaml` file to generate the server structure inside a new folder called `library_app`:

```bash
java -jar swagger-codegen-cli.jar generate \
  -i openapi.yaml \
  -l python-flask \
  -o library_app
```

---

## 4. Fix Dependency Conflicts
The generated `requirements.txt` relies on an older version of `connexion` (`2.x.x`). However, default installing `flask-pymongo` will automatically upgrade Flask to `3.x.x`, causing `connexion` endpoints to crash instantly.

Navigate to the generated folder and modify `library_app/requirements.txt` to lock the components to compatible versions heavily bounded to `< 3.0.0` and `flask < 2.3.0`:

```text
connexion >= 2.6.0, < 3.0.0
connexion[swagger-ui] >= 2.6.0, < 3.0.0
python_dateutil == 2.6.0
setuptools >= 21.0.0
swagger-ui-bundle >= 0.0.2
flask < 2.3.0
werkzeug < 2.3.0
flask-pymongo < 3.0.0
pymongo == 4.16.0
python-dotenv == 1.2.2
```

Install the safe packages:
```bash
cd library_app
pip install -r requirements.txt
```

---

## 5. Fix Null Bytes Syntax Error
Swagger Codegen occasionally contains a bug where it generates empty `__init__.py` files containing invisible null bytes (`\x00`), which causes Python to explicitly crash with: `SyntaxError: source code string cannot contain null bytes`.

Run these bash commands from within `library_app` to overwrite the corrupted files with standard python comments:
```bash
echo "# swagger_server package" > swagger_server/__init__.py
echo "# swagger_server.controllers package" > swagger_server/controllers/__init__.py
```

---

## 6. Setup MongoDB Settings
Create a new file `library_app/swagger_server/.env` to hold your MongoDB Atlas URI securely:
```env
MONGO_URI=mongodb+srv://<db_user>:<db_password>@cluster0.abcde.mongodb.net/libraryBuoi7?appName=Cluster0
```

Create a new file `library_app/swagger_server/database.py` to instantiate the `flask-pymongo` wrapper:
```python
from flask_pymongo import PyMongo

mongo = PyMongo()
```

---

## 7. Initialize Configuration in `__main__.py`
Connect your newly created database components explicitly into the generated `swagger_server/__main__.py`.

Overwrite `__main__.py` with the following implementation. This also explicitly suppresses a Flask 2.3 `JSONEncoder` deprecation warning generated heavily by Swagger templates.

```python
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
    
    # Safely suppress legacy JSONEncoder DeprecationWarning
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        app.app.json_encoder = encoder.JSONEncoder

    # Setup MongoDB
    app.app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/libraryBuoi7")
    mongo.init_app(app.app)

    # Diagnostic DB ping on startup
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
```

---

## 8. Run the Application
You can now start the server natively:

```bash
python -m swagger_server
```

Open a web browser and navigate down to the interactive Swagger UI to view and test all endpoints:
**http://127.0.0.1:8080/ui/**