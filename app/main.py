from hass_handler import HassHandler

import logging

import asyncio

from rhasspyhermes.nlu import NluIntent
from rhasspyhermes_app import EndSession, HermesApp

#Some Logging Stuff
logger = logging.getLogger("Hermes_Hass_App")
log_stream = logging.StreamHandler()
log_stream.setLevel(logging.WARNING)
logger_format = logging.Formatter('%(filename)s,%(lineno)s - %(levelname)s - %(message)s')
log_stream.setFormatter(logger_format)
logger.addHandler(log_stream)

loop = asyncio.get_event_loop()
app = HermesApp("HassApp")

hass = HassHandler()

services = loop.run_until_complete(hass.ws.fetch_services())

@app.on_intent(['hassapp.' + service for service in services])
def hass_TurnOn(intent: NluIntent):
    try:
        text = hass.handle_service_intent(intent) or None
    except:
        pass
    else:
        text = "Passing no Entity is not yet supported"
    return EndSession(text)

"""
@app.on_prefix("hassapp.")
def hass_Intent(intent: NluIntent):
    return EndSession(hass.handle_intent(intent))
"""