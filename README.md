# Sunsa Smart Blinds Wand Integration
![](https://github.com/r01k/ha_sunsa/blob/master/assets/branding/logo%402x.png)
---
Monitor and control your Sunsa blinds wands from Home Assistant.

- Control the position of the blinds.
- Monitor the wands battery level.
- Monitor other wand sensors.
- See wands diagnostic info.

This custom Home Assistant component integrates the 
[Sunsa Smart Blinds Wands](https://sunsawands.com/) by leveraging the public Sunsa REST 
cloud API. All the wands in your Sunsa account will be added to Home Assistant as cover 
entities of type blind.


## Prerequisites
In order to use the Sunsa cloud API you need to activate it for your account:
1. Inside the Sunsa app, go to `Setttings` > `API Settings`  and turn on the toggle.
2. Take note of your  `API Key` and `User ID`.


## Installation
### HACS
The recommended method to install this integration is through the
[Home Assistant Community Store (HACS)](https://hacs.xyz/). Once HACS is setup, you can use
[My Home Assistant](https://www.home-assistant.io/integrations/my/) to
[automatically add the Sunsa integration repository](http://localhost:8123/hacs/repository?owner=r01k&repository=ha_sunsa&category=integration) to 
HACS, then continue on Step 5 below after restarting Home Assistant.

Or to add the integration to HACS without using My Home Assistant:

1. Inside HACS, go to `Integrations` > Click the three-dot overflow menu `⋮` on the upper 
right and click `Custom repositories`.
2. In the `Custom repositories` dialog add the repository URL 
https://github.com/r01k/ha_sunsa. For `Category` select `Integration`.
3. Click `ADD`.
4. Restart Home Assistant.
5. Go to the `Integrations` page and add the `Sunsa` integration following the 
configuration wizard. You'll need three pieces of information:
	- Your Sunsa account email. (This is only used in the integration to group the devices
   and not for authentication).
	- Your Sunsa API User ID. See [Prerequisites](#prerequisites).
	- Your Sunsa API Key. See [Prerequisites](#prerequisites).

### Manual Installation
Alternatively, you can install the integration manually (advanced). You don't need HACS to
do this but then managing 
integration updates must be done manually too.
1. Download the `sunsa` folder in the Master branch of the GitHub repository: 
https://github.com/r01k/ha_sunsa/tree/master/custom_components/sunsa.
2. Copy the `sunsa` folder to the `custom_components` folder in your Home Assistant 
system.
3. Restart Home Assistant.
4. Continue on step 5 under [HACS](#hacs).

## FAQ
- *The blinds close the wrong way.*
  
  Ensure that the `Default Smart Home Direction` setting of the wand in the Sunsa app 
  indicates the default closing direction.

- *I added/deleted new wands on my Sunsa account. How do I update Home Assistant?*

  If you added new wands, reload the integration for them to be added automatically. 
  If wands were removed from your Sunsa account, they'll be marked `unavailable` in Home 
  Assistant and you can delete them manually.

- *There is a delay for the wands to move and for Home Assistant to update the status.*

  This is expected as per the polling interval of 20 seconds recommended by Sunsa. All 
  cloud-polling integrations present some delay.

## Troubleshooting
This integration was developed and tested with several wands of model SUNSA SW1. Correct 
functionality is not guaranteed with different (maybe older) models. In any case, 
open an issue here if you see any problem. Ensure that the wands have up-to-date firmware
and always enable debug logging for the integration when troubleshooting:
```
logger:
  default: info
  logs:
    custom_components.sunsa: debug
```

Enjoy!
