import asyncio
from hass_websocket_client import hass_websocket_client

class aobject(object):
    async def __new__(cls, *a, **kw):
        instance = super().__new__(cls)
        await instance.__init__(*a, **kw)
        return instance

    async def __init__(self):
        pass

class hass_entity_handler(aobject):
    async def __init__(self, ws):
        self.ws = ws
        self.domains = await self.__fetch_domains()
    
    async def __fetch_domains(self) -> list:
        domains = []
        tracer, manifest = await self.ws.fetch_manifest()
        if tracer:
            for entry in manifest:
                domains.append(entry['domain'])
            return domains
        else:
            return []
        self.domains = domains

    async def handle_entity_id(self, word:str, room:str = "$ALL", user:str = "$ALL"):
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
        pass