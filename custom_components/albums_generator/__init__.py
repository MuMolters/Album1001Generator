from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_PROJECT_IDENTIFIER,
    DOMAIN,
    SERVICE_RATE_ALBUM,
)
from .coordinator import AlbumsGeneratorCoordinator

PLATFORMS: list[Platform] = [
    Platform.SELECT,
    Platform.SENSOR,
]


async def async_setup(
    hass: HomeAssistant,
    _config: ConfigType,
) -> bool:
    """Register integration actions."""

    async def async_rate_album(call: ServiceCall) -> None:
        project_identifier = call.data[CONF_PROJECT_IDENTIFIER]
        coordinators = [
            coordinator
            for coordinator in hass.data.get(DOMAIN, {}).values()
            if coordinator.project_identifier.casefold()
            == project_identifier.casefold()
        ]

        if not coordinators:
            raise HomeAssistantError(
                f"No configured project matches "
                f"'{project_identifier}'."
            )

        await coordinators[0].async_rate_latest_album(
            call.data["rating"],
            call.data.get("notes", ""),
            call.data.get("generated_album_id"),
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_RATE_ALBUM,
        async_rate_album,
        schema=vol.Schema(
            {
                vol.Required(CONF_PROJECT_IDENTIFIER): str,
                vol.Required("rating"): vol.All(
                    vol.Coerce(float),
                    vol.In((1, 2, 3, 4, 5)),
                    vol.Coerce(int),
                ),
                vol.Optional("notes", default=""): str,
                vol.Optional("generated_album_id"): str,
            }
        ),
    )

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up 1001 Albums Generator from a config entry."""
    coordinator = AlbumsGeneratorCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok