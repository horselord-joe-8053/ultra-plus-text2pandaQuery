from flask import Flask
from flask_cors import CORS

from config.settings import load_config
from config.logging_config import setup_logging, get_logger
from query_syn.engine import QuerySynthesisEngine
from api.routes import register_routes


# Set up centralized logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)


def create_app() -> Flask:
    config = load_config()
    rag_system = QuerySynthesisEngine(config)
    app = Flask(__name__)
    CORS(app)
    register_routes(app, rag_system)
    return app


app = create_app()


if __name__ == '__main__':
    config = load_config()
    logger.info(f"Starting API on port {config.port}")
    app.run(host='0.0.0.0', port=config.port, debug=False)