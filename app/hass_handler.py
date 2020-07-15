from hass_websocket_client import HassWsClient

from rhasspyhermes.nlu import NluIntent
from typing import Optional
import asyncio

loop = asyncio.get_event_loop()

URL = "ws://localhost:8123/api/websocket"
TOKEN = "exampletoken123456789"
STANDARDSERVICES = ["turn_on","turn_off","toggle","update_entity"]

def extract_slot_value(slots: list, slot_name: str, default=None):
    slot = next(filter(lambda slot: slot.slot_name == slot_name, slots), None)
    if slot and slot.value["kind"] is not "Unknown":
        return slot.value.get("value", default)
    return default

class HassHandler:
    def __init__(self):
        self.ws = HassWsClient(URL,token = TOKEN)
        #{'serviceX':{'domains'=['domain1','domain2'], 'required_fields':['slot1', 'slot2']}}
        self.local_services = {}
        #Task management is going to happen here in the future
        loop.run_until_complete(self.update_local_data())

    async def handle_service_intent(self, intent):
        # one/two of entity, room, user must be passed to
        slots: dict = intent.slots
        entity_flag, entity_id, domain = self.inspect_entity(slots.get('entity',None),room=slots.get('room',None),user=slots.get('user',None))
        #TODO find out where to find intent name
        service = intent.intentName
        try:
            service_flag, nescessary_fields = self._approve_service(service, domain)
        except:
            service_flag = False
        
        if entity_flag and service_flag:
            service_data = {}
            for field in nescessary_fields:
                try:
                    service_data[str(field)] = slots[str(field)]
                except:
                    #TODO specify this for multiple missing fields
                    return "Some essential Information is missing."
            tracer = await self.ws.call_service(domain, service, service_data = service_data)
            if tracer:
                pass#All Successfull
            else:
                return "Could you rephrase your request?"

    
    def inspect_entity(self, entity:str, room:str = "$ALL", user:str = "$ALL")->(bool,str,str):
        """Checks if the passed string is a valid entity_id otherwise tries to convert it.
        Parameters
        ----------
        entity : str
            the string which is handled
        Returns
        -------
        bool
            if the returned entity_id is valid
        str
            the valid entity_id
        str
            the domain of the entity_id
        Raises
        ------
        """
        # This will do 3 Checks:
        # 1 - Check if its a actuall entity_id and if it exists in your homeassistant instance
        # 2 - Look for synonyms
        # 2.1 - Check for room/user restrictions/hints
        # 2.2 - Use domain: $ALL synonyms

        #Option 1: Valid Entity_id is passed directly
        try:
            domain = entity.split(".")[0]
            if domain in self.domains and entity in self.entity_ids:
                return (True, entity, domain)
        except:
            pass
        #Option 2: Synonym checking
        pass

    def _approve_service(self, service: str, domain: str)->(bool, list):
        try:
            service_item = self.local_services[service]
            if domain in service_item['domains']:
                #FIXME This can throw an exception
                required_fields = service_item['req_fields']
                return (True, required_fields)
        except:
            pass
        return (False, None)
    
    async def __format_fetch_services(self):
        formatted_services = {}
        flag, services = self.ws.fetch_services()
        if flag:
            for domain in services:
                for service in services[domain]:
                    if not formatted_services[service]['domains']:
                        formatted_services[service]['domains'] = []
                    formatted_services[service]['domains'].append(domain)
                    #TODO write req field per domain

    async def update_local_data(self):
        tracer, domains = await self.ws.fetch_domains()
        self.domains = domains if tracer else []
        tracer, entity_ids = await self.ws.fetch_entity_ids()
        self.entity_ids = entity_ids if tracer else []