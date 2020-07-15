import asyncio
import websockets
import json

import logging

from typing import Union

logger = logging.getLogger("Hermes_Hass_App")
class ParameterError(Exception):
    pass

class IdMissmatchError(Exception):
    pass

#TODO Secure websocket client
class HassWsClient:
    """
    A class used to handle interactions with a homeassistant instance using Websocket
    ...

    Attributes
    ----------
    __id_count : int
        a counter for generating continously increasing ID's
    url : str
        url of the homeassistant instance
    token : str
        access token to the homeassistant instance
    password: str
        password for authenticating with a older HASS.io version (Will be deprecated soon)
    """

    def __init__(self, url: str, **kwargs):
        """
        !!!a token or password MUST be provided!!!

        Parameters
        ----------
        url : str
            url of the homeassistant instance
        token : str, optional
            access token to the homeassistant instance.
        password : str, optional
            password for authenticating with older homeassistant versions (Will be deprectaed soon)
        
        Raises
        ------
        ParameterError
            if no token and no password is provided
        """
        self.__id_count = 0
        self.url = url
        if 'token' in kwargs:
            self.token = kwargs['token']
        elif 'password' in kwargs:
            self.password = kwargs['password']
        #Raise Error if neither is passed
        else:
            raise ParameterError("no Token or Password was provided")
    
    def __id_generator(self):
        """Incrementing the __id_count attribute
        Returns
        -------
        int
            the new ID
        """
        self.__id_count += 1
        return self.__id_count
    
    async def connect(self, autoauth = True):
        """Connecting to the Homeassistant Instance
        Parameters
        ----------
        autoauth : bool, optional
            if the authentication should be initiated automatically (default is True)
        
        Raises
        ------
        InvalidUrl
            the Url is faulty
        InvalidHandshake
            the websocket connection couldn't be established due to -> message
        """
        try:
            self.websocket = await websockets.connect(self.url)
        except websockets.InvalidURI:
            logging.exception("WS:InvalidURL Exception occured")
        except websockets.InvalidHandshake:
            logging.exception("WS: Handshake Error occured")
        response = json.loads(await self.websocket.recv())
        if response['type'] != 'auth_ok' and autoauth:
            await self.authenticate()

    async def authenticate(self):
        """Authenticating the client with the homeassistant instance  
        """
        if self.token:
            response = await self.__send('auth', disable_id = True, access_token=self.token)
        else:
            #The Password Authentication is going to be disconinued in the near future
            response = await self.__send('auth', disable_id = True, api_password=self.password)
        if response['type'] == 'auth_ok': logger.info("Authentication Succesfull")
        if response['type'] == 'auth_invalid': logger.info(response['message'])
    
    """
    !!! This stuff are the first test for using a recieving loop in combination with asyncio
    Sending and recieving Data is being split and therefore needs aditional handeling.

    __singular_queue = [] # [1,3,25]
    __singular_response = {} # {1:response,2:response}
    __retained_queue = {} # {2:callback, 2345:callback}
    async def _run_Recv_Loop(self):
        #THIS IS NOT RECOMMENDED AND NEEDS TESTING
        while True:
            #this is the pause while everything else runs...
            response = json.loads(await self.websocket.recv())
            id = response['id']
            singular_flag = False
            for index, item in enumerate(self.__singular_queue):
                if id == item:
                    del self.__singular_queue[index]
                    self.__singular_response[id] = response
                    singular_flag = True
                    break
            if singular_flag:
                continue
            for index, key, value in enumerate(self.__retained_queue):
                if id == key:
                    value()

    async def _send_loop(self, type: str, disable_id = False, **kwargs):
        payload_dict = {}
        if not disable_id: payload_dict["id"] = self.__id_generator()
        payload_dict["type"] = type
        #For importing all extra arguments
        for key, value in kwargs.items():
            if value is not None: payload_dict[key] = value
        payload_json = json.dumps(payload_dict)
        try:
            await self.websocket.send(payload_json)
        except TypeError as e:
            print('Unsupported Input: '+ str(e))
        except:
            print("An exception occurred")
    
    async def __await_singular(self, id: int):
        while True:
            response = self.__singular_response.pop(id, False)
            if response is False:
                await asyncio.sleep(1)
                continue
            else:#Its a hit
                return response

"""
    #I know i could override the websockets class method but this was easier
    async def ping(self) -> bool:
        """Ping Pong Websocket heartbeat
        Returns
        -------
        bool
            depending on if the heartbeat was successfull
        """
        response = await self.__send('ping')
        if response['type'] == 'pong':
            return True
        return False

    async def __send(self, type: str, disable_id = False, **kwargs):
        """sends a message via Websocket using validation features provided by homeassistant
        Parameters
        ----------
        type : str
            the type argument in every message
        disable_id : bool, optional
            if no ID should be included in the message (default = False)
        Keyword Arguments
        -----------------
        All keyword arguments passed will result in a additional key with value in the message (if not None)
        Returns
        -------
        dict
            the returned json as a dict
        Raises
        ------
        TypeError
            If the Input is unsupported
        """
        #Standard Input Values
        payload_dict = {}
        if not disable_id: payload_dict["id"] = self.__id_generator()
        payload_dict["type"] = type
        #For importing all extra arguments
        for key, value in kwargs.items():
            if value is not None: payload_dict[key] = value
        payload_json = json.dumps(payload_dict)

        try:
            await self.websocket.send(payload_json)
            response = json.loads(await self.websocket.recv())
            if disable_id or (response['id'] == payload_dict["id"] and response['type'] == 'result'):
                return response
            else:
                logger.error("A message sync issue occured")

        except TypeError as e:
            logger.exception('Unsupported Input: '+ str(e))
        except:
            logger.exception("An exception occurred")

    def __list_return(self, response) -> (bool,list):
        """This generalizes the return Statement to (bool, list)
        Parameters
        ----------
        response : dict
            the response from the Home assistant API
        Returns
        -------
        (bool,list)
            A Bool indicating if the request was successfull with the List containing either data or error
        """
        return (response['success'], response['result'] if 'result' in response.keys() else ['error',response['error']])

    def __dict_return(self, response) -> (bool,dict):
        """This generalizes the return Statement to (bool, dict)
        Parameters
        ----------
        response : dict
            the response from the Home assistant API
        Returns
        -------
        (bool,dict)
            A Bool indicating if the request was successfull with the Dictionary containing either data or the error
        """
        return (response['success'], response['result'] if 'result' in response.keys() else {'error':response['error']})

    async def call_service(self, domain: str, service: str, service_data = None) -> bool:
        """
        Parameters
        ----------
        domain : str
            domain at which the service is called (such as light or switch)
        service : str
            the service to call (such as turn_on)
        service_data : dict, optional
            additional service data (default = None)
        Returns
        -------
        bool
            True if call was successfull
        """
        response = await self.__send("call_service",domain = domain, service = service,service_data = service_data)
        return True if response['success'] else False
    
    async def fetch_states(self) -> (bool, list):
        """This will get a dump of all the current states in Home Assistant.
        Returns
        -------
        bool
            if the request was successfull
        list
            containing the responses
        """
        response  = await self.__send("get_states")
        return self.__list_return(response)
    
    async def fetch_config(self) -> (bool, dict):
        """This will get a dump of the current config in Home Assistant.
        Returns
        -------
        bool
            if the request was successfull
        dict
            containing the config
        """
        response  = await self.__send("get_config")
        return self.__dict_return(response)
    
    async def fetch_services(self) -> (bool, dict):
        """This will get a dump of the current services in Home Assistant.
        Returns
        -------
        bool
            if the request was successfull
        dict
            all services
        """
        response  = await self.__send("get_services")
        return self.__dict_return(response)
    
    async def fetch_panels(self) -> (bool, list):
        """This will get a dump of the current registered panels in Home Assistant.
        Returns
        -------
        bool
            if the request was successfull
        list
            containing the panels
        """
        response  = await self.__send("get_panels")
        return self.__list_return(response)
    
    async def fetch_media_player_thumbnail(self, entity_id: str) -> (bool, dict):
        """Return a b64 encoded thumbnail of a camera entity.
        Returns
        -------
        bool
            if the request was successfull
        dict
            containing the response {"content_type": "image/jpeg", "content" : "<base64 encoded image>"}
        """
        response  = await self.__send("media_player_thumbnail", entity_id = entity_id)
        return self.__dict_return(response)
    
    """
    From Here on we have custom Functions apart from the standard Set to enable access to additional Data
    """
    #Areas
    async def fetch_areas(self) -> (bool, list):
        response  = await self.__send("config/area_registry/list")
        return self.__list_return(response)
    
    async def delete_area(self, area_id:str) -> (bool, Union[str,dict]):
        response = await self. __send("config/area_registry/delete", area_id = area_id)
        return (response['success'], response['result'] if 'result' in response.keys() else {'error':response['error']})
    
    async def update_area(self, area_id:str, name:str) -> bool:
        response = await self.__send("config/area_registry/update", area_id = area_id, name = name)
        return response['success']
    
    async def create_area(self, name:str) -> (bool, dict):
        response = await self.__send("config/area_registry/create", name = name)
        return (response['success'], response['result'] if 'result' in response.keys() else {'error':response['error']})
    
    #Entities
    async def fetch_entity_registry(self) -> (bool, list):
        response = await self.__send("config/entity_registry/list")
        return self.__list_return(response)
    
    async def fetch_entity_ids(self) -> (bool,list):
        """Helper for entity_id fetching
        Returns
        -------
        bool
            if the fetch was successfull
        list
            containing the entity Ids
        """
        tracer, response = await self.fetch_entity_registry()
        entity_list = []
        if tracer:
            for entry in response:
                entity_list.append(entry['entity_id'])
        return tracer, entity_list if tracer else response

    #Zones
    async def fetch_zones(self) -> (bool,list):
        response = await self.__send("zone/list")
        return self.__list_return(response)

    #Manifest
    async def fetch_manifest(self) -> (bool,list):
        response = await self.__send("manifest/list")
        return self.__list_return(response)
    
    async def fetch_domains(self) -> (bool,list):
        """Helper for entity_id fetching
        Returns
        -------
        bool
            if the fetch was successfull
        list
            containing the entity Ids
        """
        tracer, response = await self.fetch_manifest()
        domains = []
        if tracer:
            for entry in response:
                domains.append(entry['domain'])
        return tracer, domains if tracer else response