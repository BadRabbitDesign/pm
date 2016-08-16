from sqlalchemy import Integer, Column, create_engine, ForeignKey, String , DateTime, Boolean, Date
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session,  backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound


import datetime
import bcrypt
import sys

import logging

from database import Base, db_session

from flask.ext.login import UserMixin


Logger = logging.getLogger(__name__)



class Projects(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name=Column(String(250), nullable=False)
    desc=Column(String(1024), nullable=True)
    notes=Column(String(1024), nullable=True)
    dateOpened=Column(DateTime, nullable=False)
    dateClosed=Column(DateTime, nullable=True)
    is_private=Column(Boolean,default=False)
    is_hidden=Column(Boolean,default=False)
    

    owner_id = Column(Integer, ForeignKey('actors.id'))
    owner = relationship("Actors", uselist=False)
    
    child_task = relationship("Tasks",  lazy='joined')
    actors = relationship('Actors',secondary='project_actors_link')
    
    def __init__(self, project_name,project_owner,  project_desc="",project_notes="",private=False):
        self.name=project_name
        self.desc=project_desc
        self.owner_id=project_owner.id
        self.dateOpened=datetime.datetime.now()
        self.notes=project_notes
        self.is_private=private
    
    @staticmethod
    def newProject(project_name,project_owner,  project_desc="",project_notes="",private=False):
        Logger.info("Project.newProject")
        _project=None
        try:
            _project=Projects(project_name,project_owner , project_desc,project_notes,private)
            db_session.add(_project)
            db_session.commit()
        except:
            Logger.exception("Project.newProject")
                
        return _project
        
    @staticmethod 
    def GetProjects():
        return Projects.query.all()     
        
    @staticmethod
    def getProjectBy_ID(_id):
        Logger.info("Project.getProjectBy_ID")
        _project=None
        try:
            _project=Projects.query.filter(Projects.id==_id).one()  
        except:
            Logger.exception("Project.getProjectBy_ID")
        
        return  _project  
        
    def all_children(self, session):
        Logger.info("Project.all_children")
        children=None
        try:
            children=db_session.query(Tasks).filter(Tasks.project_id==self.id).all()
        except:
            Logger.exception("Project.all_children")
        
        return children
        
    def GetChildTasks(self):
        Logger.info("Project.GetChildTasks")
        _tasks=None
        try:
           _tasks=db_session.query(Tasks).filter(Tasks.project_id==self.id).filter(Tasks.parent_id==None).all()
        except:
            Logger.exception("Project.GetChildTasks")
        return _tasks
        
    def setActors(self,actors):
        Logger.info("Project.setActors")
        try:
            self.actors=actors
            db_session.commit()
        except:
            Logger.exception("Project.setActors")
       
        
        
    def update(self):
        Logger.info("Project.update")
        try:
            db_session.commit()
        except:
            Logger.exception("Project.update")
        
        
        
     

class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name=Column(String(250), nullable=False)
    desc=Column(String(2048), nullable=True)
    dateOpened=Column(DateTime, nullable=False)
    dateDue=Column(DateTime, nullable=True)
    dateClosed=Column(DateTime, nullable=True)
    priority=Column(Integer, nullable=True)
    risk=Column(Integer, nullable=True)
    md = Column(Integer, nullable=True)
    is_hidden=Column(Boolean,default=False)
    strikeOut=Column(Boolean)
    
    closed_id=Column(Integer, ForeignKey('closedAs.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('tasks.id'))
    owner_id = Column(Integer, ForeignKey('actors.id'))
    
    child_comment = relationship("Comments")
    sub_task = relationship("Tasks",lazy="joined",join_depth=6)
    
    project = relationship("Projects", backref=backref('tasks', order_by=id))
    actors = relationship('Actors',secondary='task_actors_link')
    
    def __init__(self, task_name,owner_actor,task_desc="No Description", task_actors=[],dateDue=None,priority=None,risk=None,md=None):
        self.name=task_name
        self.desc=task_desc
        self.dateOpened=datetime.datetime.now()
        self.hidden=False
        self.strikeOut=False
        self.priority=priority
        self.dateDue=dateDue
        self.actors=task_actors
        self.owner_id=owner_actor.id
        self.risk=risk
        self.md=md
        
        for a in task_actors:
            self.actors.append(a)
            
            
    def getOwner(self):
        return Actors.getActorBy_ID(self.owner_id)
    
    def addActor(self, _actor):
        Logger.info("Tasks.addActor")
        try:
            self.actors.append(_actor)
            db_session.commit()
        except:
            Logger.exception("Tasks.addActor")
         
         
    def setActors(self,actors):
        Logger.info("Tasks.setActors")
        try:
            self.actors=actors
            db_session.commit()
        except:
            Logger.exception("Tasks.setActors")
         
    def addComment(self, _comment,_actorId):
        Logger.info("Tasks.addComment")
        try:
            newComment=Comments(_comment, _actorId, self.id)
            db_session.add(newComment)
            db_session.commit()
        except:
            Logger.exception("Tasks.addComment")
            
        return newComment
        
        
    def update(self):
        Logger.info("Tasks.update")
        try:
            db_session.commit()
        except:
            Logger.exception("Tasks.update")
            
            
    def close(self, _actorId, _comment="Task Closed", closedAs=1):
        Logger.info("Tasks.close")
        closed = False
        try:
            sto=False
            
            for t in self.sub_task:
                if t.isOpen():
                    sto=True
            
            if sto == False:
                newComment=Comments(_comment, _actorId, self.id)
                db_session.add(newComment)
                self.dateClosed = datetime.datetime.now()
                self.closed_id = closedAs;
                db_session.commit()
                closed = True
        except:
            Logger.exception("Tasks.close")
            
        return closed
        
    def re_open(self, _actorId, _comment="Task Re-Opened"):
        Logger.info("Tasks.re_open")
        opened = False
        try:
            
            #if the parent is closed, it will be re-opened
            Logger.info("Tasks.re_open parent =%s"%(self.parent_id))
            if self.parent_id is not None:
                
                parent=Tasks.getTaskBy_ID(self.parent_id)
                if parent.isOpen() == False:
                    parent.re_open(_actorId,_comment="Sub Task Re-Opened, Bubble-up")
                    
            
            
            newComment=Comments(_comment, _actorId, self.id)
            db_session.add(newComment)
            self.dateClosed = None
            self.closed_id = None;
            db_session.commit()
            opened = True
        except:
            Logger.exception("Tasks.re_open")
            
        return opened
         
    def isOpen(self):
        return (self.dateClosed is None)
         
         
    def getinfo(self):
        Logger.info("Tasks.getinfo")
        desc=None
        try:
            t=self
            while t.parent_id != None:
                t=Tasks.query.filter(Tasks.id==t.parent_id).one()
                desc=t.name+" / "+desc
            
            desc="""<font color="red">"""+t.project.name+"""</font>"""+" / "+desc
        except:
            Logger.exception("Tasks.getinfo")
        
        return desc
            
         
    def getTaskStatus(self):
        x = 0
        due_in = 0
        
        
        if self.dateClosed is not None:
            x=0
        else:
            x=1
            if self.dateDue is not None:
                due_in=(self.dateDue-datetime.datetime.now()).days
            else:
                due_in=0
            
        Logger.info("Tasks.getTaskStatus %s=%s"%(self.name,x))
        return (x,due_in)
    
    
    def getAllSubTaskStatus(self):
        n=0
      
        
        def get_st(t):
            st=[]
            if t.sub_task is not None:
               
                for t in t.sub_task:
                    st.append(t)
                    st.extend(get_st(t))
                    
            
            return st       
  
            
        t=self
        ast=get_st(t) 
        
        late=0
        latest=sys.maxint
        
        if len(ast)>0:
            n=len(ast)
            for s in ast:
                x,due=s.getTaskStatus()
                if due<latest:
                    latest=due
                    
                if due<0 :
                    late=late+1
                

                
        return n,late,latest
            
                
         
    
    @staticmethod
    def newTask( parent,owner_actor,task_name,task_desc = "", task_actors = [],dateDue = None,priority=None,risk=None,md=0):
        Logger.info("Tasks.newTask")
        _task=None
        try:
            
            
            _task=Tasks(task_name,owner_actor,task_desc, task_actors,dateDue,priority,risk,md)
            
            
            
            if isinstance(parent,Projects):
                Logger.info ("add task to project id=%d"%(parent.id))
                parent.child_task.append(_task)
                _task.project_id=parent.id
            elif isinstance(parent,Tasks):
                Logger.info ("add task as sub task id=%d"%(parent.id))
                parent.sub_task.append(_task)
                _task.project_id=parent.project_id
                
            else:
                raise()
            
            db_session.add(_task)
            db_session.commit()
            
            Logger.info ("new task id=%d"%(_task.id))
            
            newComment=Comments("Task Created", owner_actor.id, _task.id)
            db_session.add(newComment)
            db_session.commit()
            
            
        except:
            Logger.exception("Tasks.newTask")
            _task=None
                
        return _task
    
        
         
    @staticmethod
    def getTaskBy_ID(_id):
        Logger.info("Tasks.getTaskBy_ID")
        task=None
        try:
            task=Tasks.query.filter(Tasks.id==_id).one()
        except:
            Logger.exception("Tasks.getTaskBy_ID")
            
        return task
        
     
    def GetCloseOptions(self):
        return ClosedAs.query.all()      
        
        
    def get_project(self):
        prj=None
        Logger.info("Tasks.get_project")
        try:
            prj=self.Project
        except:
            Logger.exception("Tasks.get_project")
            
        return prj
            
        

class Comments(Base):
    __tablename__ = 'comments'
    id      = Column(Integer, primary_key=True)
    comment =Column(String(4096))
    date    =Column(DateTime, nullable=False)
    is_hidden=Column(Boolean,default=False)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    actor_id = Column(Integer, ForeignKey('actors.id'))
    task    = relationship("Tasks", backref=backref('comments', order_by=id))
  
    def __init__(self, _content, _actor_id, _task_id):
        self.comment=_content.lstrip()
        self.task_id=_task_id
        self.actor_id=_actor_id
        self.date=datetime.datetime.now()
        
        
    @staticmethod
    def addComment(_content, _actorId, _taskId):
        Logger.info("Comments.addComment")
        newComment=None
        try:
            newComment=Comments(_content.lstrip(), _actorId, _taskId)
            db_session.add(newComment)
            db_session.commit()
        except:
            Logger.exception("Comments.addComment")
        
        return newComment
        
        
    def getActorName(self):
        Logger.info("Comments.getActorName")
        name=None
        try:
            actor=Actors.getActorBy_ID(self.actor_id)
            if actor:
                name=actor.name
                
        except:
            Logger.exception("Comments.getActorName")
        return name
    
    
        
  
class Actors(UserMixin,Base):
    __tablename__ = 'actors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    user_name = Column(String(250), nullable=False)
    email= Column(String(250), nullable=True)
    password= Column(String(250), nullable=False)
    role=Column(Integer, nullable=False)
    
    is_verified=Column(Boolean)
    is_frozen=Column(Boolean)
    is_hidden=Column(Boolean,default=False)
    
    
    
    projects = relationship('Projects',secondary='project_actors_link')
    tasks = relationship('Tasks',secondary='task_actors_link')
    
    
    @staticmethod
    def addNewActor(user_name,email,name=None):
        Logger.info("Actors.addNewActor [name:%s email:%s]"%(name,email))
        try:
            _actor=Actors()

            _actor.user_name=user_name
            
            if name is None:
                _actor.name=first_name
            else:
                _actor.name=name
            
            _actor.email=email
            _actor.password=bcrypt.hashpw("password", bcrypt.gensalt(14))
            _actor.is_verified=False
            _actor.is_frozen=False
            _actor.role=0x07
            db_session.add(_actor)
            db_session.commit()

        except:
            Logger.exception("Actors.addNewActor")
            
    @staticmethod 
    def GetAllActors():
        return Actors.query.all()     
        
    
    def verify_password(self, password):
        Logger.info("Actors.verify_password")
        verified=False
        try:
            pwhash = bcrypt.hashpw(password.encode('utf-8'), self.password.encode('utf-8')).decode()
            verified=(self.password == pwhash)

        except:
            Logger.exception("Actors.verify_password")

        return verified

    
    
    def set_password(self, password):
        Logger.info("Actors.set_password")
        done=False
        try:
            hashed = bcrypt.hashpw(password, bcrypt.gensalt(14))
            self.password=hashed
            db_session.commit()
            done=True
        except:
            Logger.exception("Actors.set_password")
            
        return done
        
        
    
    @staticmethod
    def getActorBy_Name(_name):
        Logger.info("Actors.getActorBy_Name [%s]"%_name)
        
        actor = None
        try:
            actor = Actors.query.filter(Actors.name==_name).one()
        except MultipleResultsFound, e:
            Logger.exception( "Actors.getActorBy_Name Multiple Results Found")	
            pass
            # Deal with it
        except NoResultFound, e:
            Logger.exception( "Actors.getActorBy_Name no result")
            pass
            # Deal with that as well
        
        return actor
        
        
    @staticmethod
    def getActorBy_ID(_id):
        Logger.info("Actors.getActorBy_ID [%s]"%_id)
        actor=''
        try:
            actor = Actors.query.filter(Actors.id==_id).one()
        except MultipleResultsFound, e:
            Logger.exception( "Actors.getActorBy_ID Multiple Results Found")	
            # Deal with it
        except NoResultFound, e:
            Logger.exception( "Actors.getActorBy_ID no result")
            # Deal with that as well
        
        return actor
        
        
    def checkRoles(self,requestedRoles):
        roles=[]
        if self.role and 0x01 ==0x01:
            roles.append('user')
        if self.role  and 0x02 ==0x02:
            roles.append('pm')
        if self.role  and 0x04 ==0x04:
            roles.append('admin')
            
        for r in requestedRoles:
            if r in roles:
                return True
        return False
            
        
            
class ProjectActorsLink(Base):
    __tablename__ = 'project_actors_link'
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    actor_id = Column(Integer, ForeignKey('actors.id'), primary_key=True)


class TaskActorsLink(Base):
    __tablename__ = 'task_actors_link'
    Task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True)
    actor_id = Column(Integer, ForeignKey('actors.id'), primary_key=True)


class ClosedAs(Base):
    __tablename__ = 'closedAs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    
    
    @staticmethod
    def addCosedAsType(name):
        Logger.info("ClosedAs.addCosedAsType [name:%s]"%(name))
        try:
            _tbl=ClosedAs()
            _tbl.name=name
            db_session.add(_tbl)
            db_session.commit()

        except:
            Logger.exception("ClosedAs.addCosedAsType")
            
            
      
    
    @staticmethod
    def byId(val):
        return ClosedAs.query.filter(ClosedAs.id==val).one()
    
    
    
    

if __name__ == '__main__':
    engine = create_engine('sqlite:///pm.db')
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(engine)
