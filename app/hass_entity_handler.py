import asyncio
from hass_websocket_client import hass_websocket_client

class hass_entity_handler():
    def __init__(self, ws:hass_websocket_client):
        self.ws = ws
    
    async def update_external_data(self):
        tracer, domains = await self.ws.fetch_domains()
        self.domains = domains if tracer else []
        tracer, entity_ids = await self.ws.fetch_entity_ids()
        self.entity_ids = entity_ids if tracer else []

    async def _approve_entity_id(self, entity_id) -> bool:
        return True if entity_id in self.entity_ids else False

    async def handle_entity_id(self, word:str, room:str = "$ALL", user:str = "$ALL")->(bool,str,):
        """Checks if the passed string is a valid entity_id and tries to convert it.
        Parameters
        ----------
        word : str
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

        #Option 1: Valid Entity_id
        try:
            domain = word.split(".")[0]
            if domain in self.domains and self._approve_entity_id(word):
                return (True, word)
        except:
            pass