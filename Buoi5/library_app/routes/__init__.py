from routes.book_routes import book_bp
from routes.loan_routes import loan_bp
from routes.user_routes import user_bp


def apply_routes(app):
    """Register all blueprints on the Flask application."""
    app.register_blueprint(user_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(loan_bp)
