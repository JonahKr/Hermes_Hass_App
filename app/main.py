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

def extract_slot_value(intent: NluIntent, slot_name: str, default=None):
    slot = next(filter(lambda slot: slot.slot_name == slot_name, intent.slots), None)
    if slot and slot.value["kind"] is not "Unknown":
        return slot.value.get("value", default)
    return default

@app.on_intent("hassapp.TurnOn")
def hass_TurnOn(intent: NluIntent):
    entity = extract_slot_value(intent, "entity")
    #room = extract_slot_value(intent, "room")
    #user = extract_slot_value(intent, "user")
    if entity:
        text = hass.handle_service_intent(intent) or None
    else:
        text = "Passing no Entity is not yet supported"
    return EndSession(text if not entity else None)

"""
@app.on_prefix("hassapp.")
def hass_Intent(intent: NluIntent):
    return EndSession(hass.handle_intent(intent))
"""