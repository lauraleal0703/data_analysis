class Config:
    VERSION = "0.0.1"
    NAME = "Análisis de datos"
    URL = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "1!-jduZa9-9@d89-6"

class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 9400
    LIFETIME = 100000

class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    HOST = "127.0.0.1"
    PORT = 80
    LIFETIME = 120


config = {
    "production": ProductionConfig,
    "development": DevelopmentConfig
}