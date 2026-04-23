from middleware.deprecation import register_deprecation_after_request
from routes.v1.payment_routes import payment_v1_bp
from routes.v2.payment_routes import payment_v2_bp
from versioning.dispatcher import dispatcher_bp


def apply_routes(app):
    """Register all blueprints and attach deprecation middleware to v1."""
    app.register_blueprint(payment_v1_bp)
    app.register_blueprint(payment_v2_bp)
    app.register_blueprint(dispatcher_bp)

    # Attach deprecation headers to every response from the v1 blueprint
    register_deprecation_after_request(app, "payment_v1")
