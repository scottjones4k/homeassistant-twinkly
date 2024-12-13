"""Twinkly integration"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_NAME, CONF_HOST
from homeassistant.core import HomeAssistant
from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.LIGHT]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Oura from a config entry."""
    host: str = entry.data[CONF_HOST]
    name: str = entry.data[CONF_NAME]

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "name": name,
        "host": host
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True