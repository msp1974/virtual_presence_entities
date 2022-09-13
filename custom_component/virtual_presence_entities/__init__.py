"""The Virtual Presence Entities integration."""
from __future__ import annotations
import asyncio

import json
import logging
from time import sleep

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback, Event
from homeassistant.helpers.event import async_track_state_change_event

from homeassistant.helpers import area_registry, device_registry, entity_registry

from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Virtual Presence Entities from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)
    handler = VirtualEntityController(hass)
    hass.data[DOMAIN][entry.entry_id] = handler

    handler.go()
    

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class VirtualEntityController():
    def __init__(self, hass):
        self._hass = hass
        #self._hass.async_create_task(self.getAreaList(hass))
        self._location_entity = "sensor.last_alexa"
        self._active_area = ""

    def go(self):
        state = "media_player.lounge_echo" #self.get_entity_state(self._location_entity)
        #_LOGGER.warning(state)
        #_LOGGER.warning(self.get_entity_area(state))
        #_LOGGER.warning(self.get_alexa_entities())
        #_LOGGER.warning(self.get_entities_by_area(self.get_entity_area(state), "lamps"))

        unsub = async_track_state_change_event(self._hass, self.get_alexa_entities(), self.alexa_event_handler)

    @callback
    def alexa_event_handler(self, event: Event):
        #if event.data.new_state.last_called != None:
        if event.data.get('new_state').attributes.get('last_called'):
            self._active_area = self.get_entity_area(event.data.get('entity_id'))
            _LOGGER.warning(f"Area: {self._active_area}")

    async def async_entity_action_handler(self, entity_class, action, **kwargs):
        # Get entty item in area
        _LOGGER.warning(f"Active Area: {self._active_area}, Class: {entity_class}, Action: {action}, KWARGS: {kwargs}")
        entity_id = self.get_entities_by_area(self._active_area, entity_class)
        _LOGGER.warning(entity_id)



    async def getAreaList(self, hass):
        areas = area_registry.async_get(hass).areas
        for area in areas:
            _LOGGER.warning(area)

    def get_entity_from_entity_id(self, entity: str):
        """Get wiser entity from entity_id"""
        domain = entity.split(".", 1)[0]
        entity_comp = self._hass.data.get("entity_components", {}).get(domain)
        _LOGGER.warning(f"{domain}, {entity_comp}")
        if entity_comp:
            return entity_comp.get_entity(entity)
        return None

    def get_entity_state(self, entity_id: str):
        #entity = self.get_entity_from_entity_id(entity_id)
        #return entity.state
        return self._hass.states.get(entity_id)

    def get_entity_area(self, entity_id: str):
        entity = entity_registry.async_get(self._hass).async_get(entity_id)
        if entity.area_id == None:
            device = device_registry.async_get(self._hass).async_get(entity.device_id)
            return device.area_id
        return entity.area_id

    def get_devices_by_area(self, area: str):
        dr = device_registry.async_get(self._hass)
        return device_registry.async_entries_for_area(dr, area)

    def get_entities_by_area(self, area: str, filter: str | list[str] = ""):
        device_ids = [ device.id for device in self.get_devices_by_area(area) ]
        #Get entities for each device if entity has no area of its own that != area
        er = entity_registry.async_get(self._hass)

        entities = [
            entity.entity_id
            for entity in er.entities.values()
            if entity.area_id == area
            and any(term in entity.entity_id.split(".")[1] for term in list(filter))
        ]

        device_entities = [
            entity.entity_id
            for entity in er.entities.values()
            if entity.device_id in device_ids
            and entity.area_id is None
            and any(term in entity.entity_id.split(".")[1] for term in list(filter))
        ]

        return entities + device_entities



    def get_alexa_entities(self):
        er = entity_registry.async_get(self._hass)
        return [
            entity.entity_id
            for entity in er.entities.values()
            if entity.platform == 'alexa_media'
            and entity.entity_id.split(".")[0] == "media_player"
        ]

