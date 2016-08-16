# This snippet is in public domain.
# However, please retain this link in your sources:
# http://flask.pocoo.org/snippets/120/
# Danya Alexeyevsky

from flask import session, redirect, current_app,request,url_for
from functools import wraps


#cfg = current_app.config.get
#cookie = cfg('REDIRECT_BACK_COOKIE', 'back')
#default_view = cfg('REDIRECT_BACK_DEFAULT', 'index')

cookie='back'
default_view='main.project_manager'



    
def anchor(func, cookie=cookie):
    @wraps(func)
    def result(*args, **kwargs):
        session[cookie] = request.url
        return func(*args, **kwargs)
    return result

   
def url(default=default_view, cookie=cookie):
    return session.get(cookie, url_for(default))

    
def redirect(default=default_view, cookie=cookie):
    return redirect(url(default, cookie))

