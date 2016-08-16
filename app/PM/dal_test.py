
import logging
logging.basicConfig()


import sqlalchemy
import sys
from sqlalchemy import Integer, Column, create_engine, ForeignKey, String
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import string
import random
from random import randint
import config
import database
from models import *



def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))




def addSomeUsers():
    _actors=["caspar","susan","josh","frank","dougal","murphy","bill","ben","paul","george"]
    for x in _actors:
        print("adding ...%s"%x)
        _name=x
        _email='%s@myLittlePony.eu' %(_name)
        _user_name=x

        Actors.addNewActor(_user_name,_email,_name)
     



def addSomeProjects():
    
    nprojects=10
    
   
    _actors=Actors.GetAllActors()
    
    
    for x in range(nprojects): 
    
        _name="PROJECT_%s" % id_generator(10)  
        _desc=id_generator(10)  
        
        print("adding project %s : %s"%(_name,_desc))
        
        _project=Projects.newProject(_name,random.choice(_actors) ,  project_desc=_desc,project_notes="no Notes",private=False)
  
        
        #generate randomised acess of actors
        act=[y for y in range(len(_actors))]
        random.shuffle(act)
        
        #add random number of actors to a poject
        prj_actors=[]
        for a in range(randint(0, 5)): 
            prj_actors.append(_actors[act[a]])
            
        _project.setActors(prj_actors)
            
            
            
        for t in range(randint(2, 5)):
           
            actors_in_project=_project.actors
            
            ta=actors_in_project[0:randint(0,len(actors_in_project) )]
            
            print("adding task ....")
            
            task_name=("TASK_%d_%d_%s"%(x,t,  _project.name))
            _task=Tasks.newTask( _project,random.choice(_actors),task_name,task_desc = "description", task_actors = [],dateDue = None,priority=None)
            
            
            
            for s in range(randint(2, 5)):
                st_name=("SUB_TASK_%d_%d_%d_%s"%(x,t,s,  _task.name))
                Tasks.newTask( _task,random.choice(_actors),st_name,task_desc = "sub task", task_actors = [],dateDue = None,priority=None)
                print("adding sub task ........")
            
 
def AddClosedAs():
    reasons=["Finished","Stopped - No Longer Required","Stopped - Requirements Changed"]
    for r in reasons:
        print("AddClosedAs :%s"%r)
        ClosedAs.addCosedAsType(r)
   



if __name__ == '__main__':
    
    print sqlalchemy.__version__ 
    
    
   
    database.init_db()
 
    print("session:%s"%database.db_session)
    
    if True:
        database.Base.metadata.drop_all(bind=database.engine) 
        database.Base.metadata.create_all(database.engine)
        addSomeUsers()
        addSomeProjects()
        AddClosedAs()
   
    
    
    my_actors=database.db_session.query(Actors).all()
    print my_actors
    

    if False:

        for p in database.db_session.query(Projects):
            print ("P_%s  owner=%s"%(p.name, p.owner.name))
            
            for a in p.actors:
                print ("->A_%s_%s"%(a.name, a.email))
            
            
            for t in p.tasks:
                print ("\t->>T_%s" %(t.name))
                for st in t.sub_task:
                    print ("\t\t->>>ST_%s" %(st.name))
                    
            print
            print
        
        
        print "============================================="
        for a in database.db_session.query(Actors):
             print "Actor = %s" %a.name
             print("Projects...")
             for p in a.projects:
                 print "P::%s" %p.name
             print
             print("tasks...")    
             for t in a.tasks:
                 print "T::%s" %t.name
             print
             print
        pass 
    
