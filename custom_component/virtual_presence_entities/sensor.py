"""Support for Virtual light via Alexa"""
import asyncio
import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass, SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        AlexaLastArea(hass, data, "Last Alexa Area")
    ]
    async_add_entities(sensors, True)


class AlexaLastArea(SensorEntity):
    """Alexa Last Area Sensor Object."""

    def __init__(self, hass, data, name):
        """Initialize the sensor."""
        self._data = data
        self._hass = hass
        self._name = name
        self.current_area = ""

    async def async_update(self):
        """Async Update method ."""
        _LOGGER.debug(f"{self.name} Sensor Update requested")

    @property
    def name(self):
        """Return the name of the Device.""" 
        return self._name

    @property
    def state(self):
        return self.current_area.title()
 
    @property
    def unique_id(self):
        return f"{DOMAIN}-{self._name}"

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    """
    @property
    def device_info(self):
        Return device specific attributes.
        return {
                "name": "Virtual Light 1",
                "identifiers": "VL001",
                "manufacturer": "Virtual Light",
                "model": "VL1",
                "sw_version": "NA",
                "serial_number" : "123435",
                "product_type": "Light",
                "product_identifier": "VL1",
                "via_device": "VLC01",
            }
    """

    async def async_added_to_hass(self):
        """Subscribe for update from the hub."""

        async def async_update_state(data):
            """Update sensor state."""
            self.current_area = data.get("area")
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{DOMAIN}-AreaUpdateMessage", async_update_state
            )
        )
