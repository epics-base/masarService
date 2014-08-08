'''
Created on Jul 25, 2014

@author: shengb
'''
import mongoengine as me
__configdb = "service_config"
__eventdb = "service_event"

class ServiceConfig(me.Document):
    """Configuration for MASAR service."""
    cid = me.IntField(primary_key=True, unique=True, required=True)
    name = me.StringField(max_length= 50, unique=True, required=True)
    desc = me.StringField(max_length=255, required=False)
    system = me.StringField(max_length=255, required=True)
    status = me.StringField(max_length=255, required=True)
    version = me.IntField()
    createdate = me.DateTimeField()
    
    # place to hold a list of pvs belong to given configuration
    # each pv could be name and description.
    pvlist = me.DictField()
        
class ServiceEvent(me.DynamicDocument):
    """Event happened to capture one snapshot with given configuration."""
    eid = me.IntField(primary_key=True, unique=True, required=True)
    configid = me.IntField(required=True)
    comment = me.StringField(max_length=255)
    createdate = me.DateTimeField()
    status = me.IntField(required=True)
    username = me.StringField(max_length=50)
    
    # data field to store data from IOC. 
    masardata=me.DictField()
