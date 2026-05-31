from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # ============= VALIDATE ENVIRONMENT VARIABLES =============
    required_env_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing critical environment variables: {', '.join(missing_vars)}")
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
    
    # Database URL - make it optional for testing
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Fallback to SQLite for development if no DB URL provided
        database_url = 'sqlite:///travelo_dev.db'
        logger.warning("DATABASE_URL not set. Using SQLite for development.")
    
    # ============= CONFIGURE APP =============
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    # Determine allowed origins based on environment
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5500')
    cors_origins = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        frontend_url
    ]
    
    # Add production origins if not in development
    if os.getenv('FLASK_ENV') != 'development':
        production_url = os.getenv('PRODUCTION_FRONTEND_URL')
        if production_url:
            cors_origins.append(production_url)
    
    # Remove duplicates and filter empty strings
    cors_origins = list(set([url for url in cors_origins if url]))
    
    logger.info(f"CORS origins configured: {cors_origins}")
    
    # ============= INITIALIZE EXTENSIONS =============
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # ============= REGISTER BLUEPRINTS =============
    try:
        from app.routes.auth import auth_bp
        from app.routes.preferences import preferences_bp
        from app.routes.recommendations import recommendations_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(preferences_bp, url_prefix='/api')
        app.register_blueprint(recommendations_bp, url_prefix='/api')
        
        logger.info("All blueprints registered successfully")
    except ImportError as e:
        logger.error(f"Failed to import blueprints: {str(e)}")
        raise
    
    # ============= ERROR HANDLERS =============
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return {"error": "Internal server error"}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {"error": "Bad request"}, 400
    
    return app