#!/usr/bin/env python
import os
from app.pm import create_app
import random, string
from flask_debugtoolbar import DebugToolbarExtension
import datetime
from flask.ext.mail import Mail



pm= create_app ('development')
mail=Mail(pm)

@pm.template_global(name='GetRandomString')
def GetRandomString(N=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


@pm.template_global(name='isZero')
def isZero(n):
    return (n==0)


    
@pm.template_filter('dateFilter')
def _jinja2_filter_datetime(date, fmt=None):
    format='%b %d, %Y'
    return date.strftime(format) 



def run():
    toolbar = DebugToolbarExtension()
    toolbar.init_app(pm)
    pm.run()

if __name__=='__main__':

    toolbar = DebugToolbarExtension()
    toolbar.init_app(pm)
    port = int(os.environ.get("PORT", 5000))
    pm.run(host='0.0.0.0', port=port)
    
