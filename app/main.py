from hass_handler import HassHandler

import logging
 
import asyncio

from rhasspyhermes.nlu import NluIntent
from rhasspyhermes_app import EndSession, HermesApp

#Some Logging Stuff
logger = logging.getLogger("Hermes_Hass_App")
logger.setLevel(logging.DEBUG)
log_stream = logging.StreamHandler()
log_stream.setLevel(logging.WARNING)
logger_format = logging.Formatter('%(filename)s,%(lineno)s - %(levelname)s - %(message)s')
log_stream.setFormatter(logger_format)
logger.addHandler(log_stream)

loop = asyncio.get_event_loop()
app = HermesApp("HassApp")

hass = HassHandler(loop)

services = loop.run_until_complete(hass.ws.fetch_services())
#['hassapp.' + str(service) for service in services]
@app.on_intent('hassapp.turn_on')
async def hass_Intent(intent: NluIntent):
    logger.debug("INTENT is there")
    text = ""
    try:
        logger.debug("passing on")
        #asyncio.create_task(hass.handle_service_intent(intent))
        loop.run_until_complete(hass.ws.fetch_entity_registry())

    except:
        pass
    else:
        text = "Passing no Entity is not yet supported"
    return EndSession(text)

app.run()
