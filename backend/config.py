# backend/config.py
import os
from pathlib import Path

class Config:
    '''Base configuration'''
    
    # App settings
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    TESTING = False
    
    # API settings
    API_VERSION = '1.0.0'
    API_PREFIX = '/api'
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Model paths (relative to project root)
    BASE_DIR = Path(__file__).parent.parent
    HYPATIAX_DIR = BASE_DIR / 'hypatiax'
    MODELS_DIR = HYPATIAX_DIR / 'data_spacy' / 'queries' / 'tableau'
    
    NER_DESC_MODEL = str(MODELS_DIR / 'ner_tableau_desc')
    NER_FORMULA_MODEL = str(MODELS_DIR / 'ner_tableau_formulas')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'
    
    # Request limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size


class DevelopmentConfig(Config):
    '''Development configuration'''
    DEBUG = True


class ProductionConfig(Config):
    '''Production configuration'''
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    '''Testing configuration'''
    TESTING = True
    DEBUG = True


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    '''Get configuration based on environment'''
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
