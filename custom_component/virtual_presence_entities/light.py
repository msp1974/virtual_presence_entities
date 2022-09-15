"""Support for Virtual light via Alexa"""
import asyncio
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityFeature
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    virtual_lights = [
        VirtualLight(hass, data, "Lights", ["light","lights"]),
        VirtualLight(hass, data, "Lamps", ["lamp", "lamps"]),
        VirtualLight(hass, data, "Fan", ["fan", "fans"])
    ]
    async_add_entities(virtual_lights, True)


class VirtualLight(LightEntity):
    """Virtual Light Object."""

    def __init__(self, hass, data, name, terms):
        """Initialize the sensor."""
        self._data = data
        self._is_on = True
        self._hass = hass
        self._name = name
        self._terms = terms

    async def async_update(self):
        """Async Update method ."""
        _LOGGER.debug(f"{self.name} Light Update requested")

    @property
    def supported_features(self):
        """Flag supported features."""
        return 1

    @property
    def supported_color_modes(self) -> set[ColorMode] | set[str] | None:
        return ColorMode.BRIGHTNESS

    @property
    def is_on(self):
        """Return the boolean response if the node is on."""
        return False

    @property
    def brightness(self):
        """Return the brightness of this light between 0..100."""
        return 0

    @property
    def name(self):
        """Return the name of the Device.""" 
        return self._name

 
    @property
    def unique_id(self):
        return f"VL001-{self._name}"

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


    async def async_turn_on(self, **kwargs):
        """Turn light on."""
        """
        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS])
            await self.hass.async_add_executor_job(
                setattr, self._device, "current_percentage", round((brightness / 255) * 100)
            )
        else:
            await self.hass.async_add_executor_job(
                self._device.turn_on
            )
        await self.async_force_update()
        """
        await self._data.async_entity_action_handler(self._terms, "async_turn_on", **kwargs)
        _LOGGER.warning(f"TURN ON: {kwargs}")
        return True

    async def async_turn_off(self, **kwargs):
        """Turn light off."""
        """
        await self.hass.async_add_executor_job(
            self._device.turn_off
        )
        await self.async_force_update()
        """
        await self._data.async_entity_action_handler(self._terms, "async_turn_off", **kwargs)
        _LOGGER.warning("TURN OFF", kwargs)

    """
    async def async_added_to_hass(self):
        Subscribe for update from the hub.

        async def async_update_state():
            Update light state.
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._data.wiserhub.system.name}-HubUpdateMessage", async_update_state
            )
        )
    """