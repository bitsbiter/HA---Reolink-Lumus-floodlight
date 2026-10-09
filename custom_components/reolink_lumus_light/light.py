"""Floodlight van de Reolink Lumus via Baichuan cmd 288 / push cmd 291."""

from datetime import timedelta
import logging

from reolink_aio.exceptions import ReolinkError

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo

from . import REOLINK_DOMAIN, loaded_reolink_entries

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)  # leest alleen de gecachte status, geen netwerkverkeer
CHANNEL = 0
DURATION = 180  # seconden dat de camera de lamp aan houdt na een aan-commando
SUPPORTED_MODELS = {"Reolink Lumus"}

SET_FLOODLIGHT_XML = """
<?xml version="1.0" encoding="UTF-8" ?>
<body>
<FloodlightManual version="1.1">
<channelId>{channel}</channelId>
<status>{state}</status>
<duration>{duration}</duration>
</FloodlightManual>
</body>"""


async def async_setup_entry(hass, config_entry, async_add_entities) -> None:
    """Maak een lamp voor elke Reolink-camera die zijn spotlight niet aanmeldt."""
    entities = []
    for reolink_entry in loaded_reolink_entries(hass):
        host = reolink_entry.runtime_data.host
        api = host.api
        if api.model in SUPPORTED_MODELS and not api.supported(CHANNEL, "floodLight"):
            entities.append(LumusFloodlight(reolink_entry.entry_id, host.unique_id))
    async_add_entities(entities)


class LumusFloodlight(LightEntity):
    """Aan/uit-lamp op het bestaande Reolink-apparaat."""

    _attr_has_entity_name = True
    _attr_name = "Floodlight"
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_should_poll = True

    def __init__(self, reolink_entry_id: str, host_unique_id: str) -> None:
        self._reolink_entry_id = reolink_entry_id
        self._attr_unique_id = f"{host_unique_id}_lumus_floodlight"
        self._callback_id = f"lumus_light_{host_unique_id}"
        # Zelfde identifier als de officiële integratie: entiteit komt op hetzelfde apparaat.
        self._attr_device_info = DeviceInfo(identifiers={(REOLINK_DOMAIN, host_unique_id)})
        self._attr_is_on = False
        self._registered_on = None

    @property
    def _api(self):
        """Haal het actuele Host-object op (verandert als de Reolink-entry herlaadt)."""
        entry = self.hass.config_entries.async_get_entry(self._reolink_entry_id)
        if entry is None or entry.state is not ConfigEntryState.LOADED:
            return None
        return entry.runtime_data.host.api

    @property
    def available(self) -> bool:
        api = self._api
        return api is not None and api.session_active

    @callback
    def _push_callback(self) -> None:
        """Push cmd 291 ontvangen: status staat al in de cache van reolink-aio."""
        if (api := self._api) is not None:
            self._attr_is_on = api.whiteled_state(CHANNEL)
            self.async_write_ha_state()

    def _ensure_callback(self) -> None:
        """(Her)registreer de push-callback op het actuele Baichuan-object."""
        api = self._api
        if api is None or self._registered_on is api.baichuan:
            return
        api.baichuan.register_callback(self._callback_id, self._push_callback, 291, CHANNEL)
        self._registered_on = api.baichuan

    async def async_added_to_hass(self) -> None:
        self._ensure_callback()

    async def async_will_remove_from_hass(self) -> None:
        if self._registered_on is not None:
            self._registered_on.unregister_callback(self._callback_id)

    async def async_update(self) -> None:
        """Vangnet: callback opnieuw koppelen na een herlaad en status overnemen."""
        self._ensure_callback()
        api = self._api
        if api is not None and "state" in api._whiteled_settings.get(CHANNEL, {}):
            self._attr_is_on = api.whiteled_state(CHANNEL)

    async def _set(self, state: bool) -> None:
        api = self._api
        if api is None:
            raise HomeAssistantError("Reolink-integratie is niet geladen")
        xml = SET_FLOODLIGHT_XML.format(channel=CHANNEL, state=int(state), duration=DURATION)
        try:
            await api.baichuan.send(cmd_id=288, channel=CHANNEL, body=xml)
        except ReolinkError as err:
            raise HomeAssistantError(f"Floodlight schakelen mislukt: {err}") from err
        self._attr_is_on = state
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        await self._set(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._set(False)
