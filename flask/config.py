SECTRT_KEY = "popacatapetal"

class Config(object):
    #delay: Logging intervalin seconds 600 is 10 minutes
    DELAY = 600
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    AREA_NAME ='Garage'
    PRESSURE_MIN = 940
    PRESSURE_MAX = 1053

class Production(Config):
    SECRET_KEY = 'newexternalsecret'

