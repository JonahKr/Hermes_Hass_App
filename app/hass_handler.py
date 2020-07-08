from hass_websocket_client import HassWsClient

import asyncio

loop = asyncio.get_event_loop()

URL = "ws://localhost:8123/api/websocket"
TOKEN = "exampletoken123456789"
STANDARDSERVICES = ["turn_on","turn_off","toggle","update_entity"]

class HassHandler:
    def __init__(self):
        self.ws = HassWsClient(URL,token = TOKEN)
        #Task management is going to happen here in the future
        loop.run_until_complete(self.update_external_data())

    
    def handle_service_call(self, entity: str, service:str, **kwargs):
        tracer, entity_id, domain = self.inspect_entity(entity, room = None, user = None)
        if tracer:
            #TODO replace with approving function
            if service in STANDARDSERVICES:
                domain = "homeassistant"
            loop.run_until_complete(self.ws.call_service(domain,service,service_data={entity_id:entity}))
        else:
            return "No valid Entity Id got passed. Sorry!"
    
    def inspect_entity(self, entity:str, room:str = "$ALL", user:str = "$ALL")->(bool,str,str):
        """Checks if the passed string is a valid entity_id and tries to convert it.
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

    async def update_external_data(self):
        tracer, domains = await self.ws.fetch_domains()
        self.domains = domains if tracer else []
        tracer, entity_ids = await self.ws.fetch_entity_ids()
        self.entity_ids = entity_ids if tracer else []