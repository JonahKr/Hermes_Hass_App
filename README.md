# Hermes_Hass_App
A Full Home Assistant integration for the Hermes Protocoll.

This Project has the Goal to fully integrate Home Assistant with the Hermes Protocoll...
This includes:
- a Websocket client connecting to the hass instance
- entity synonym handling to enable simple conversion from: Kitchenlamp to light.kitchen_ceiling
- Room specific entity matching: If you say turn on the lamp in the kitchen, the kitchen lamp will turn on
- User specific entity matching: "Turn on MY lights please"
- Prefered Devices: Settings to controll devices without specific information needed
- Automatic Intent and Slot generator tailored to your Home Assistant services
- Service Name Matching to keep the number of intents as small as possible
- Fetching entity/device data: "What temperature is the living room at?"
...

Lets see where this goes