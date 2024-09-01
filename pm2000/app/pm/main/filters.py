from . import main
from jinja2 import pass_eval_context 
from markupsafe import Markup,escape
import re

import logging
Logger = logging.getLogger(__name__)

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')



#@main.app_template_filter()
#@evalcontextfilter
#def nl2br(eval_ctx, value):
#    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '\n<br>') \
#        for p in _paragraph_re.split(escape(value)))
#    
#    if eval_ctx.autoescape:
#        result = Markup(result)
#    return result
    
    

@main.app_template_filter()
@pass_eval_context 
def nl2br(eval_ctx, value):
   _paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
   result = u'\n\n'.join(u'<p>%s</p>' % p.replace(u'\r\n', u'<br/>') for p in _paragraph_re.split(value))
   if eval_ctx.autoescape:
       result = Markup(result)
   return result
    

    
@main.app_template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    
    return date.strftime('%d, %b %Y @ %H:%M')
        
