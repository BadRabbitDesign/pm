from flask.ext.wtf import Form
from wtforms import StringField,TextAreaField,SubmitField,BooleanField,DateField,SelectField,HiddenField,PasswordField,IntegerField
from wtforms.validators import Required

PRIORITY_CHOICES=[(0, 'Low'), (1, 'Norm'), (2, 'Urgent'), (3, 'Critical')]
RISK_CHOICES=[(0, 'L'), (1, 'L+'), (2, 'M-'), (3, 'M'), (4, 'M+'), (5, 'H-'), (6, 'H'), (7, 'U')]

class FormProject(Form):
    name=StringField('Name',validators=[Required(message=u'*')])
    description=TextAreaField('Description',validators=[Required(message=u'*')])
    owner=StringField('Owner',validators=[Required(message=u'*')])
    is_private=BooleanField('is Private?')
    is_hidden=BooleanField('is Hidden?')
    notes=TextAreaField('Notes')
    pid=HiddenField('pid')
    
class FormTask(Form):
    name=StringField('Name',validators=[Required(message=u'*')])
    description=TextAreaField('Description')
    owner=StringField('Owner',validators=[Required(message=u'*')])
    dateDue=DateField('Due Date',validators=[Required(message=u'*')])
    duration=IntegerField('Estimated MD',default=0)
    priority=SelectField(u'Priority', choices=PRIORITY_CHOICES, coerce=int)
    risk=SelectField(u'Risk', choices=RISK_CHOICES, coerce=int)
    is_hidden=BooleanField('is Private?') 
    comment=TextAreaField('Add Comment')   
    
    
class LoginForm(Form):
    username=StringField('UserName')
    password=PasswordField('Password')
    remember_me=BooleanField('keep me logged in')
    submit=SubmitField('Log-in')
    next=HiddenField('next')
    

    
        
