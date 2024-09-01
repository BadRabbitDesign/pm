from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField,BooleanField,DateField,SelectField,HiddenField,PasswordField,IntegerField
from wtforms.validators import DataRequired

PRIORITY_CHOICES=[(0, 'Low'), (1, 'Norm'), (2, 'Urgent'), (3, 'Critical')]
RISK_CHOICES=[(0, 'L'), (1, 'L+'), (2, 'M-'), (3, 'M'), (4, 'M+'), (5, 'H-'), (6, 'H'), (7, 'U')]

class FormProject(FlaskForm):
    name=StringField('Name',validators=[DataRequired(message=u'*')])
    description=TextAreaField('Description',validators=[DataRequired(message=u'*')])
    owner=StringField('Owner',validators=[DataRequired(message=u'*')])
    is_private=BooleanField('is Private?')
    is_hidden=BooleanField('is Hidden?')
    notes=TextAreaField('Notes')
    pid=HiddenField('pid')
    
class FormTask(FlaskForm):
    name=StringField('Name',validators=[DataRequired(message=u'*')])
    description=TextAreaField('Description')
    owner=StringField('Owner',validators=[DataRequired(message=u'*')])
    dateDue=DateField('Due Date',validators=[DataRequired(message=u'*')])
    duration=IntegerField('Estimated MD',default=0)
    priority=SelectField(u'Priority', choices=PRIORITY_CHOICES, coerce=int)
    risk=SelectField(u'Risk', choices=RISK_CHOICES, coerce=int)
    is_hidden=BooleanField('is Private?') 
    comment=TextAreaField('Add Comment')   
    
    
class LoginForm(FlaskForm):
    username=StringField('UserName')
    password=PasswordField('Password')
    remember_me=BooleanField('keep me logged in')
    submit=SubmitField('Log-in')
    next=HiddenField('next')
    

    
        
