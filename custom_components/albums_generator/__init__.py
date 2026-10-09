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
        project_identifier = call.data.get(CONF_PROJECT_IDENTIFIER)
        generated_album_id = call.data.get("generated_album_id")
        select_entity_id = call.data.get("select_entity_id")
        if select_entity_id is not None:
            selected_state = hass.states.get(select_entity_id)
            if selected_state is None:
                raise HomeAssistantError(
                    f"Album selector '{select_entity_id}' was not found."
                )

            selected_project = selected_state.attributes.get(
                CONF_PROJECT_IDENTIFIER
            )
            if not isinstance(selected_project, str):
                raise HomeAssistantError(
                    "The selected album selector has no project "
                    "identifier."
                )
            if (
                project_identifier is not None
                and selected_project.casefold()
                != project_identifier.casefold()
            ):
                raise HomeAssistantError(
                    "The selected album does not belong to the "
                    "specified project."
                )
            project_identifier = selected_project

            selected_generated_id = selected_state.attributes.get(
                "generated_album_id"
            )
            if not isinstance(selected_generated_id, str) or not (
                selected_generated_id
            ):
                raise HomeAssistantError(
                    "Choose an unrated album in the album selector "
                    "before submitting a rating."
                )
            if (
                generated_album_id is not None
                and generated_album_id != selected_generated_id
            ):
                raise HomeAssistantError(
                    "The provided album ID does not match the album "
                    "selected in the selector."
                )
            generated_album_id = selected_generated_id

        if not isinstance(project_identifier, str) or not (
            project_identifier
        ):
            raise HomeAssistantError(
                "Provide a project identifier or an album selector entity."
            )

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
            generated_album_id,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_RATE_ALBUM,
        async_rate_album,
        schema=vol.Schema(
            {
                vol.Optional(CONF_PROJECT_IDENTIFIER): str,
                vol.Required("rating"): vol.All(
                    vol.Coerce(float),
                    vol.In((1, 2, 3, 4, 5)),
                    vol.Coerce(int),
                ),
                vol.Optional("notes", default=""): str,
                vol.Optional("generated_album_id"): str,
                vol.Optional("select_entity_id"): str,
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