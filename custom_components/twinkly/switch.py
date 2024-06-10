import logging
import time

import voluptuous as vol

from homeassistant.components.switch import (SwitchDevice, PLATFORM_SCHEMA)
from homeassistant.const import (CONF_HOST, CONF_NAME)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import device_registry as dr

REQUIREMENTS = ['pytwinkly==0.1.6']

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Twinkly Switch'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the TPLink switch platform."""
    from pytwinkly.twinkly import TwinklyClient
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    client = TwinklyClient(host)
    auth = await client.authenticate()
    device_info = None
    if auth:
        device_info = await client.get_device_info()
    async_add_entities([TwinklySwitch(client, name, device_info)], True)


class TwinklySwitch(SwitchDevice):
    """Representation of a Twinkly switch."""

    def __init__(self, twinkly, name, device_info):
        """Initialize the switch."""
        self.twinkly = twinkly
        self._name = name
        self._state = None
        self._available = device_info != None
        self.device_details = device_info

    @property
    def name(self):
        """Return the name of the Smart Plug, if any."""
        return self._name

    @property
    def available(self) -> bool:
        """Return if switch is available."""
        return self._available

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self.authenticate()
        if self._available:
            await self.twinkly.turn_on()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self.authenticate()
        if self._available:
            await self.twinkly.turn_off()

    async def async_update(self):
        """Update the Twinkly switch's state."""
        try:
            await self.authenticate()
            if self._available:
                self._state = await self.twinkly.is_on()

        except ConnectionError as ex:
            if self._available:
                _LOGGER.warning(
                    "Could not read state for %s: %s", self.name, ex)
                self._available = False

    async def authenticate(self):
        try:
            authenticated = await self.twinkly.authenticate()
            self._available = authenticated

        except ConnectionError as ex:
            if self._available:
                _LOGGER.warning(
                    "Could not read state for %s: %s", self.name, ex)
                self._available = False
    @property
    def unique_id(self):
        """Return a unique ID."""
        return self.device_details['uuid']

    @property
    def device_info(self):
        return {
            'identifiers': {
                # Serial numbers are unique identifiers within a specific domain
                ('Twinkly', self.unique_id)
            },
            'connections': {
                (dr.CONNECTION_NETWORK_MAC, self.device_details['mac'])
            },
            'name': self.name,
            'manufacturer': 'Ledworks',
            'model': self.device_details['product_code'],
            'sw_version': self.device_details['product_version'],
        }
