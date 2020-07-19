from tinydb import TinyDB, Query
from hass_websocket_client import hass_websocket_client
from typing import Union
import json

db_path = "../synonym_db.json"
"""
Filestructure:
$ALL:
    $ALL:
    User1:
    User2:
Zone1:
    $ALL:
    User2:

"""
class hass_synonym_db:
    def __init__(self, ws: hass_websocket_client):
        self.ws = ws
        self.db = TinyDB(db_path)
        self.zone_query = Query()
    
    def new_zone(self, zone_name: str) -> (bool,Union(str,None)):
        req: list = self.db.search(self.zone_query.name == zone_name)
        if len(req) > 0:
            return (False, "This Zone already exists")
        else:
            self.db.insert({'name':zone_name, 'user':{'$ALL':{}}})
            return True
    
    def delete_zone(self, zone_name: str):
        self.db.remove(self.zone_query.name == zone_name)
    
    def update_zone(self, zone_name: str, new_zone_name: str):
        self.db.update({'name': new_zone_name}, self.zone_query.name == zone_name)
    
    def is_zone(self,zone_name: str) -> bool:
        pass
    
    def new_synonym(self, entity_id: str, synonym: str, zone: str = '$ALL', user: str = '$ALL'):
        self.db.insert()