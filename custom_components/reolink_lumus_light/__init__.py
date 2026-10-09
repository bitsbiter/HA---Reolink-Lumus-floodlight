"""Lamp-entiteit voor Reolink-camera's die hun spotlight niet aanmelden.

Hergebruikt de Baichuan-verbinding (TCP 9000) van de officiële Reolink-integratie
en stuurt cmd 288 (FloodlightManual). Status komt binnen via push cmd 291.
"""

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

DOMAIN = "reolink_lumus_light"
REOLINK_DOMAIN = "reolink"
PLATFORMS = [Platform.LIGHT]


def loaded_reolink_entries(hass: HomeAssistant) -> list[ConfigEntry]:
    """Geef alle geladen config entries van de officiële Reolink-integratie."""
    return [
        entry
        for entry in hass.config_entries.async_entries(REOLINK_DOMAIN)
        if entry.state is ConfigEntryState.LOADED and hasattr(entry, "runtime_data")
    ]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Wacht tot de Reolink-integratie geladen is en zet de lamp op."""
    if not loaded_reolink_entries(hass):
        raise ConfigEntryNotReady("Reolink-integratie is nog niet geladen")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Verwijder de lamp."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
