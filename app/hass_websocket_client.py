import asyncio
import websockets
import json

class ParameterError(Exception):
    pass

class IdMissmatchError(Exception):
    pass

#TODO Secure websocket client
#TODO Version restrictions from HomeAssistant (for example the Camera stuff is getting deprecated)
class hass_websocket_client:
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
        FIXME Exceptions from the websockets library aren't handled
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
        self.websocket = await websockets.connect(self.url)
        response = json.loads(await self.websocket.recv())
        if response['type'] != 'auth_ok' and autoauth:
            await self.authenticate()

    async def authenticate(self):
        """Authenticating the client with the homeassistant instance
        TODO Implement Logger instead of print    
        """
        if self.token:
            response = await self.__send('auth', disable_id = True, access_token=self.token)
        else:
            #The Password Authentication is going to be disconinued in the near future
            response = await self.__send('auth', disable_id = True, api_password=self.password)
        if response['type'] == 'auth_ok': print("Authentication Succesfull")
        if response['type'] == 'auth_invalid': print(response['message'])
    
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
                #TODO handle where ids don't match for whatever reason
                #raise Exception("The returned Id ("+str(response['id'])+") from the API does not match the sended one"+str(payload_dict["id"])
                print("i hate this")
        except TypeError as e:
            print('Unsupported Input: '+ str(e))
        except:
            print("An exception occurred")

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
        return (response['success'], response['result'] if 'result' in response.keys() else [])
    
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
        return (response['success'], response['result'] if 'result' in response.keys() else [])
    
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
        return (response['success'], response['result'] if 'result' in response.keys() else {})
    
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
        return (response['success'], response['result'] if 'result' in response.keys() else [])
    
    async def fetch_camera_thumbnail(self, entity_id: str) -> (bool, dict):
        """Return a b64 encoded thumbnail of a camera entity.
        Returns
        -------
        bool
            if the request was successfull
        dict
            containing the response {"content_type": "image/jpeg", "content" : "<base64 encoded image>"}
        """
        response  = await self.__send("camera_thumbnail", entity_id = entity_id)
        return (response['success'], response['result'] if 'result' in response.keys() else {})
    
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
        return (response['success'], response['result'] if 'result' in response.keys() else {})
    
    """
    From Here on we have custom Functions apart from the standard Set to enable access to additional Data
    """

    #AREAS
    async def fetch_areas(self) -> (bool, list):
        response  = await self.__send("config/area_registry/list")
        return (response['success'], response['result'] if 'result' in response.keys() else [])