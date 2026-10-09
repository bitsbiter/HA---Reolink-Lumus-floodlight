"""Config flow: geen instellingen, alleen een entry aanmaken."""

from homeassistant.config_entries import ConfigFlow

from . import DOMAIN


class ReolinkLumusLightFlow(ConfigFlow, domain=DOMAIN):
    """Maak één config entry aan."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Start vanuit de UI."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Reolink Lumus floodlight", data={})
