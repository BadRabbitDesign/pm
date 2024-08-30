import os
basedir=os.path.abspath(os.path.dirname(__file__))



#SQLALCHEMY_DATABASE_URI    = os.environ['DATABASE_URL']
SQLALCHEMY_DATABASE_URI     = "postgresql://localhost/pm2000"
#SQLALCHEMY_DATABASE_URI    = 'sqlite:///pm.db'


class Config:
    SECRET_KEY= "gjlkfgjjlkfjgjrigjjh5668598u5gjjhyjghjkjk445jkygt"
	
    PERMANENT_SESSION_LIFETIME      = 3600
    SESSION_PERMANENT               = False
    LOGGER_NAME                     = "projectManagerLogger"
    TITLE                           = "PM2000"

    TASK_LATE       = 0.0
    TASK_IMENENT    = 5.0
    TASK_DUE        = 11.0
   
    #images to use
    BAD_PERMISSION_IMAGE    = 'images/finger-wag-sync.gif'
    TITLE_IMAGE             = 'images/goat_1.png'
    TASK_DONE_IMAGE         = 'images/TICK-SMALL.png'
    TASK_FUTURE_IMAGE       = 'images/TL-BLUE-SMALL.png'
    TASK_DUE_IMAGE          = 'images/TL-YELLOW-SMALL.png'
    TASK_IMENENT_IMAGE      = 'images/TL-ORANGE-SMALL.png'
    TASK_LATE_IMAGE         = 'images/TL-RED-SMALL.png'
    
    USE_LOCAL_JQUERY        = True
    SORRY_MESSAGE           = "Sorry something went wrong, report it to admin if it happens again"
    
    #email
    MAIL_SERVER             = 'smtp.gmail.com'
    MAIL_PORT               = 587
    MAIL_USE_TLS            = True
    MAIL_USERNAME           = 'xxxxxxxxxx'
    MAIL_PASSWORD           = 'xxxxxxxxxx'
    
    PM_MAIL_SUBJECT_PREFIX  = 'PM2000'
    PM_MAIL_SENDER          = 'NO-REPLY@gmail.com'
    

class DevelopmentConfig(Config):
    DEBUG=True
    DEBUG_TB_INTERCEPT_REDIRECTS    = False
 


config={
	'development': DevelopmentConfig,
	'default': DevelopmentConfig
}
