from __future__ import annotations

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = b"B!\x1d\xc6\xb8'\xd6\x97\xe9\xa0\xed\xb1\xe3\x00\xa0\xa1"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = '@o9p^R_NVK1Hkd85KnANU6yA_>Np:G}TXc_'
    SQLALCHEMY_DATABASE_URI = 'postgresql://tglvtldbsdzhmm:2905a819edc34c7573670ec5ee500307311d6ee58da98be79731d2c049faa27b@ec2-54-159-175-38.compute-1.amazonaws.com:5432/d782ee528lko56'


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
