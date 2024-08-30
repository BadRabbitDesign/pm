# -*- coding: utf-8 -*-

from . import main
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack,json,Markup,jsonify, current_app
from datetime import timedelta
import random, string
import platform
from models import Projects, Tasks, Actors, Comments, ClosedAs
from functools import wraps
from forms import FormProject, FormTask, LoginForm, PRIORITY_CHOICES, RISK_CHOICES
from wtforms import validators
from flask.ext.login import login_user,logout_user,login_required,current_user
import re
from jinja2 import evalcontextfilter, Markup, escape

from . import login_manager
import redirectback as back
#from decorators import requires_roles
import logging
import helpers

from filters import *
from app.mail import email

Logger = logging.getLogger(__name__)

SORRY_MESSAGE="SORRY_MESSAGE"



from flask.ext.cors import CORS,cross_origin

#app = Flask(__name__)
#CORS(app)


class PmError(Exception):
    def __init__(self, value):
        self.value = "PmError:"+value
    def __str__(self):
        return repr(self.value)




@login_manager.user_loader
def load_user(user_id):
    Logger.debug("load_user:%s"%user_id)
    return Actors.getActorBy_ID(user_id)



def get_current_user_role():
    return 'user'

def error_response():
    return render_template('notAllowed.html')


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if (current_user.checkRoles(roles))==False:
                return error_response()
            return f(*args, **kwargs)
        return wrapped
    return wrapper    
   


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


def getValueFromRequest(request,tag):
    val=None
    if tag in request.args:
        val=request.args.get(tag)
       
        
    Logger.debug ("Tag %s == %s"%(tag,val))
    return val   



def getValueAndStore(request,tag):
    val=None
    if tag in request.args:
        val=request.args.get(tag)
        session[tag] =val
    elif tag in session: 
        val=session[tag] 
        
    Logger.debug ("Tag %s == %s"%(tag,val))
    return val   



def getFromSession(name,on_error=None):
    return session[name] if name in session else None 

@main.before_request
def make_session_permanent():
    Logger.debug( "before request")


def updateSessionValue(_id,_val=None):
        if _val:
            Logger.debug ("%s=%s" %(_id,_val))
            session[_id]=_val
        else:
            Logger.debug("remove :%s"%(_id))
            session.pop(_id, None)

@main.after_request
def save_data_to_session(response):
    #Logger.debug("save_data_to_session")
    return response
     
@main.route('/broken', methods=['GET','POST'])    
def broken():
    return "<!DOCTYPE html><html><head>  <title>Broken</title></head><body><h1>i'm sorry something is very broken!</h1></body></html>"


@main.route('/', methods=['GET','POST'])
@login_required
def project_manager():

    try:
        Logger.debug("project_manager")
        help="""
        <b>main Project page</b>
        <ul>
        <li>Log in to do any thing usefull</li>
        </ul>
        """

                
        projects=Projects.query.all() 
            
        return render_template('pm.html', form_message='', projects=projects,help=help )
        
        
    except PmError as e:
        Logger.exception( 'Exception:project_manager [%s]'%e.value)
        flash(SORRY_MESSAGE)
       
    except :
        Logger.exception( 'Exception:project_manager [unknown]')
        flash(SORRY_MESSAGE)
        
    return redirect(url_for('.broken'))   

@main.route('/showProjectDetail', methods=['GET','POST'])
@main.route('/showProjectDetail/id/<pid>', methods=['GET','POST'])
@login_required
def showProjectDetail(pid=None):
    if True:
        project=None
        form=FormProject()

        
        #if we dont have a project id, see if its in the request object
        if pid is None:
            pid =getValueFromRequest(request,'prj')
            if pid is None:
                raise PmError("pid not defined")
            
        else:
            pass
            
        Logger.debug("showProject: %s" %(pid))

        
        if form.validate_on_submit():
            pid = form.pid.data
            project=Projects.query.filter(Projects.id==pid).one()
            Logger.debug ("updateing project")
            project.name=form.name.data
            project.desc=form.description.data
            project.notes=form.notes.data
            project.is_private=form.is_private.data
            project.is_hidden=form.is_hidden.data
            
            project.update()
            flash('Project updated')
            
        else:
            project=Projects.query.filter(Projects.id==pid).one()
            
            
        form.name.data          =project.name
        form.description.data   =project.desc
        form.owner.data         =project.owner.name
        form.is_private.data    =project.is_private
        form.is_hidden.data     =project.is_hidden
        form.notes.data         =project.notes
        form.pid.data           =pid   
        
        
        return render_template('showProject.html', project=project,form=form)
       
    try:  
        pass  
        
    except PmError as e:
        Logger.exception( 'Exception:showProjectDetail [%s]'%e.value)
        flash(SORRY_MESSAGE)
        
    except :
        Logger.exception( 'Exception:showProjectDetail [unknown]')
        flash(SORRY_MESSAGE)
    
    return redirect(url_for('.project_manager'))
        
        
@main.route('/showProjectOverview', methods=['GET','POST'])
@main.route('/showProjectOverview/id/<pid>', methods=['GET','POST'])
@login_required
def showProjectOverview(pid=None):
    if True:
        project=None
        form=FormProject()

        
        #if we dont have a project id, see if its in the request object
        if pid is None:
            pid =getValueFromRequest(request,'prj')
            if pid is None:
                raise PmError("pid not defined")
            
        else:
            pass
            
        Logger.debug("showProject: %s" %(pid))
        project=Projects.query.filter(Projects.id==pid).one()    
        return render_template('showProject_flat.html', project=project)
    
    try:  
        pass  
        
    except PmError as e:
        Logger.exception( 'Exception:showProjectOverview [%s]'%e.value)
        flash(SORRY_MESSAGE)
        
    except :
        Logger.exception( 'Exception:showProjectOverview [unknown]')
        flash(SORRY_MESSAGE)
    
    return redirect(url_for('.project_manager'))        
      
    


@main.route('/newProject', methods=['GET','POST'])
@login_required
@requires_roles('admin', 'manager')
def newProject():
    try:
        Logger.debug("newProject")
        form=FormProject()
        form.owner.data=current_user.name
        
        if  form.validate_on_submit():
            Logger.debug("newProject:form is validated")
            _name=form.name.data
            _desc=form.description.data
            _owner=form.owner.data
            _is_private=form.is_private.data
            _notes=form.notes.data 
            _actor=Actors.getActorBy_Name(_owner)
            
            if _actor is None:
                flash('user not found!')
                return redirect(url_for('.newProject'))
            
            _project=Projects.newProject(_name,_actor , _desc,project_notes=_notes,private=_is_private)
            
            if _project is None:
                flash('new project creation failed!')
            else:
                flash('new project was created')
                   
            return redirect(url_for('.project_manager'))
        elif form.is_submitted():
            Logger.debug("newProject:Form validation Failed")
            flash('Form Has Failed Validation')
        else:
            pass
            
            
            
        return render_template('newProject.html',form=form)
        
    except PmError as e:
        Logger.exception( 'Exception:newProject [%s]'%e.value)
        flash(SORRY_MESSAGE)
       
    except :
        Logger.exception( 'Exception:newProject [unknown]')
        flash(SORRY_MESSAGE)
        
    return redirect(url_for('.project_manager'))    
        

@main.route('/ModifyProjectActors', methods=['GET','POST'])
@login_required
@requires_roles('admin', 'manager')
def ModifyProjectActors():
    g.target='.ModifyProjectActors'
    pid =getValueFromRequest(request,'prj')
    g.pid=pid
    actionDesc="Get Actors For Project"
    project=Projects.query.filter(Projects.id==pid).one()
    
    
    if  request.method == 'POST':
            
        _actors=[]
        actor_ids = request.form.getlist("actors")
        
            
        if actor_ids and pid:
            project.actors=[]
            for _id in actor_ids:
            
                a=Actors.getActorBy_ID(_id)
                if a is not None:  
                    _actors.append(a)
                
        project.setActors(_actors)
        return redirect(url_for('.showProjectDetail',pid=pid))  
    
    actors=Actors.GetAllActors()
    
    _active_actors=project.actors 
    
    for a in actors:
        if a in _active_actors:
            a.checked=True
        else:
            a.checked=False
    
        
    
    return render_template('modifyActors.html',actors=actors,actionDesc=actionDesc,\
        help="""Add or Remove actors from the current project - just check or uncheck the listed actors to change who is assigned to the project"""
        )

@main.route('/ModifyTaskActors', methods=['GET','POST'])
@login_required
@requires_roles('admin', 'manager')
def ModifyTaskActors():
    g.target='.ModifyTaskActors'
    tid =getValueFromRequest(request,'tsk')
    g.tid=tid
    actionDesc="Get Actors For Task"
    task=Tasks.getTaskBy_ID(tid)
    pid=task.project_id
    
    
    if  request.method == 'POST':
            
        _actors=[]
        actor_ids = request.form.getlist("actors")
        
            
        if actor_ids and tid:
                
                task.actors=[]
                for _id in actor_ids:
                    _actor=Actors.getActorBy_ID(_id)
                    if _actor is not None:
                        _actors.append(_actor)
                
        task.setActors(_actors)
                 
        return redirect(url_for('.showTask',tid=tid))  
            
    
    
    project=Projects.query.filter(Projects.id==pid).one()
    actors=project.actors
    task=Tasks.getTaskBy_ID(tid)
    _active_actors=task.actors
    
    for a in actors:
        if a in _active_actors:
            a.checked=True
        else:
            a.checked=False
        
    
    return render_template('modifyActors.html',actors=actors,actionDesc=actionDesc,\
        help="""Add or Remove actors from the current project - just check or uncheck the listed actors to change who is assigned to the project"""
        )





@main.route('/showTask', methods=['GET', 'POST'])
@main.route('/showTask/id/<tid>', methods=['GET', 'POST'])
@login_required
def showTask(tid=None):
    if True:
    
        task=None
        due_date_changed=False
        
        form=FormTask(prefix="form_task")
        #form.owner.data = current_user.name
        
        
        if tid is None:
            tid =getValueFromRequest(request,'tsk')
            
            
        Logger.debug("showTask id:%s"%(tid))  
        
        task=Tasks.getTaskBy_ID(tid)
        
        if task is None:
            flash('no Task id found!')
            return redirect(url_for('.project_manager'))

        pid=task.project_id
        comment=""
            
        if form.is_submitted(): 
           
            comment=form.comment.data  
            
            if form.validate_on_submit():
                Logger.debug("showTask: Form is validated")
                
                ChangedMess=''
                ChangedMess+=helpers.test_ne(task.name,form.name.data,"Name changed\r\n")
                ChangedMess+=helpers.test_ne(task.desc,form.description.data,("Description changed\r\n"))
                
                ChangedMess+=helpers.test_ne(task.priority,form.priority.data,("Priority changed to: %s\r\n"% \
                    dict(PRIORITY_CHOICES).get(form.priority.data)) )
                    
                ChangedMess+=helpers.test_ne(task.risk,form.risk.data,("Risk changed to: %s\r\n"%\
                    dict(RISK_CHOICES).get(form.risk.data)) )
                    
                ChangedMess+=helpers.test_ne(task.md,form.duration.data,("Duration changed to: %s\r\n"%form.duration.data))
                    
                ChangedMess+=helpers.test_date_ne(task.dateDue,form.dateDue.data,("Due date changed to: %s\r\n" % form.dateDue.data))
                
                task.name       =form.name.data
                task.desc       =form.description.data
                task.dateDue    =form.dateDue.data
                task.priority   =form.priority.data
                task.risk       =form.risk.data
                task.md         =form.duration.data
                task.is_hidden  =form.is_hidden.data
                
                task.update()
                
                flash('Task updated')

                if len(ChangedMess):
                    Comments.addComment(ChangedMess,current_user.id,task.id)
                
                
                if len(form.comment.data) !=0:
                    commentStr=form.comment.data
            
                    if re.search('[a-zA-Z0-9]', commentStr) is not None:   
                        Comments.addComment(commentStr,current_user.id,task.id)
                        flash('comment added') 
                        comment="" 
                    
                    
            else: 
                flash('!Task update:Form Failed Validation')      
         
         
        form.owner.data         =task.getOwner().name
        form.name.data          =task.name
        form.description.data   =task.desc
        form.dateDue.data       =task.dateDue
        form.priority.data      =task.priority
        form.risk.data          =task.risk
        form.is_hidden.data     =task.is_hidden
        form.duration.data      =task.md  
        form.comment.data       =comment       
        
             
            
        return render_template('showTask.html',task=task,form=form,project_id= pid,task_id= tid)
    try:
        pass
    
    except PmError as e:
        Logger.exception( 'Exception:showTask [%s]'%e.value)
        flash(SORRY_MESSAGE)
       
    except :
        Logger.exception( 'Exception:showTask [unknown]')
        flash(SORRY_MESSAGE)
        
    return redirect(url_for('.project_manager'))   


def newTask(request,pid=None,tid=None,form=None):
    
    done=False
    
    try:
        Logger.debug("newTask")
        if form.is_submitted():

                
            if form.validate_on_submit():
                Logger.debug("newTask: Form is validated")
                _name=form.name.data
                _desc=form.description.data
                _owner=form.owner.data
                _dateDue=form.dateDue.data
                _priority=form.priority.data
                _is_hidden=form.is_hidden.data
                _risk=form.risk.data
                
                if tid:
                    parent= Tasks.getTaskBy_ID( tid)
                    pid=parent.project_id
                elif pid:
                    parent=  Projects.getProjectBy_ID(pid)
                
                task=Tasks.newTask(parent,\
                owner_actor=current_user,\
                task_name=_name,\
                task_desc=_desc,\
                task_actors=[],\
                dateDue=_dateDue,\
                priority=_priority,\
                risk=_risk  )
                
                if task is None:
                    flash('Failed to create new Task!')
                    Logger.debug("newTask: Failed")
                else:
                    done=True 
                    Logger.debug("newTask: Done ok")   
                
                
            
            else:
                flash('newTask: Failed to Validate the Form')
            
        return done
        
       
    except PmError as e:
        Logger.exception( 'Exception:newTask [%s]'%e.value)
        flash(SORRY_MESSAGE)
       
    except :
        Logger.exception( 'Exception:newTask [unknown]')
        flash(SORRY_MESSAGE)
        
    return redirect(url_for('.project_manager'))       


@main.route('/projectAddTask', methods=['GET', 'POST'])
@login_required 
@requires_roles('admin', 'manager') 
def projectAddTask(): 
    g.target='.projectAddTask'
    form=FormTask()
    pid =getValueAndStore(request,'prj')
    Logger.debug("projectAddTask :pid=%s"%pid)
    if (newTask(request,pid=pid,form=form)) == False:
        form.owner.data=current_user.name
        return render_template('newTask.html',_name = "prj",_value=pid, form = form, title = ("Parent:'%s' Project"%(Projects.getProjectBy_ID(pid).name)))
    else:
        return redirect(url_for('main.showProjectDetail', pid=pid))
        



@main.route('/TaskAddTask', methods=['GET', 'POST'])
@login_required 
@requires_roles('admin', 'manager') 
def TaskAddTask(): 
    g.target='.TaskAddTask'
    form=FormTask()
    tid =getValueAndStore(request,'tsk')
    Logger.debug("TaskAddTask :tid=%s"%tid)
    if (newTask(request,tid=tid,form=form)) == False:
        form.owner.data=current_user.name
        return render_template('newTask.html',_name = "tsk",_value=tid, form=form, title=("Parent:'%s' Task"%(Tasks.getTaskBy_ID(tid).name)))
    else:
        return redirect(url_for('.showTask', tid=tid))
        


@main.route('/TaskClose', methods=['GET', 'POST'])
@login_required 
@requires_roles('admin', 'manager')         
def TaskClose():

    tid =getValueFromRequest(request,'tsk')
    cid =getValueFromRequest(request,'cid')
    Logger.debug("TaskClose tid=%s  cid=%s" %(tid,cid))
    
    task=Tasks.getTaskBy_ID(tid)
    comment=("Task Clased as : %s"%(ClosedAs.byId(cid).name))
    
    if task is not None:
        if (task.close(current_user.id,_comment=comment,closedAs=cid)==True):
            flash("Task %s Was Closed"%(task.name))
        else:
            flash("""Task "%s" Cannot be Closed because it has open sub-tasks!"""%(task.name))
        
       
    return redirect(url_for('.showTask', tid=tid))

@main.route('/TaskReOpen', methods=['GET', 'POST'])
@login_required 
@requires_roles('admin', 'manager')         
def TaskReOpen():

    tid =getValueAndStore(request,'tsk')
    task=Tasks.getTaskBy_ID(tid)
    
    if task is not None:
        if (task.re_open(current_user.id)==True):
            flash("Task %s Was Re-Opend"%(task.name))
        else:
            flash("""Task "%s" Has Not Been re-opened, this is a Problem!"""%(task.name))
        
        
    return redirect(url_for('.showTask', tid=tid))    

@main.route('/showMyWork', methods=['GET'])
@login_required
def showMyWork():
    if True:
        Logger.debug("showMyWork")
        _actor=current_user

        _myOwnedProjects=Projects.query.filter(Projects.owner_id==_actor.id).all()
        _myWorkProjects=_actor.projects
        _myTasks=_actor.tasks
        return render_template('showMyWork.html', myOwnedProjects=_myOwnedProjects, myWorkProjects=_myWorkProjects, tasks=_myTasks)
    try: 
        pass
        
    except PmError as e:
        Logger.exception( 'Exception:showMyWork [%s]'%e.value)
        flash(SORRY_MESSAGE)
       
    except :
        Logger.exception( 'Exception:showMyWork [unknown]')
        flash(SORRY_MESSAGE)
        
    return redirect(url_for('.project_manager'))   


    
@main.route('/login',methods=['GET','POST'])
def login():
    Logger.debug("login")
    form=LoginForm()
    
    if form.is_submitted():
        Logger.debug("login:form is submitted")
    
    if form.validate_on_submit():

        Logger.debug("login: user=%s password=%s" % (form.username.data,form.password.data))
    
        _actor=Actors.getActorBy_Name(form.username.data)
        if _actor is not None and _actor.verify_password(form.password.data):
            Logger.debug("login: is authenticated")
            login_user(_actor,form.remember_me.data)
            return redirect(form.next.data or url_for('.project_manager'))
        else:
             flash('Login failed!')
            
    form.next.data=request.args.get('next')
    print next
           
    return render_template('login.html',form=form)


@main.route('/logout')
@login_required
def logout():
    Logger.debug("logout")
    logout_user()
    return redirect(url_for('.project_manager'))
    
    
    
@main.route('/new')
def new():
    return render_template('new.html')
    
    
    
  
@main.route('/test')
def test():
    email.send_email('casparlucas@hotmail.co.uk','test','simple',name="caspar")
    return redirect(url_for('.project_manager'))


#   ,---.  ,------. ,--. 
#  /  O  \ |  .--. '|  | 
# |  .-.  ||  '--' ||  | 
# |  | |  ||  | --' |  | 
# `--' `--'`--'     `--' 

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d



@main.route('/api/v0.0/get_all_projects')
@cross_origin()
def API_get_projects():
    projects=Projects.GetProjects()
    p=[]
    for prj in projects:
        p.append(row2dict(prj))
    return json.dumps(p)
    
    

@main.route('/api/v0.0/get_project_by_id/<int:pid>')
@cross_origin()
def API_get_project_by_id(pid):
    projects=Projects.getProjectBy_ID(pid)
    p=(row2dict(projects))
    return json.dumps(p)



@main.route('/api/v0.0/get_prj_tasks/<int:pid>')
@cross_origin()
def API_get_tasks(pid):
    _project=Projects.getProjectBy_ID(pid)
    tasks=_project.GetChildTasks()
    t=[]
    for tsk in tasks:
        t.append(row2dict(tsk))
    return json.dumps(t)
    
    

@main.route('/api/v0.0/get_child_tasks/<int:tid>')
@cross_origin()
def API_get_task_children(tid):
    task=Tasks.getTaskBy_ID(tid)
    st=task.sub_task
    
    t=[]
    for tsk in st:
        t.append(row2dict(tsk))
    return json.dumps(t)





















