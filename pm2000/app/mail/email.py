from threading import Thread
from flask_mail import Message
from flask import Flask, render_template,copy_current_request_context



def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)
        
def send_email(to,subject,template,**kwargs):
    from pm import pm as app
    from pm import mail
    
    
    msg = Message(app.config['PM_MAIL_SUBJECT_PREFIX']+subject,
        sender=app.config['PM_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    _thread=Thread(target=send_async_email,args=[app,msg])
    _thread.start()
    return _thread

