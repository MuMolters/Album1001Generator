from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_GROUP_SLUG,
    CONF_PROJECT_IDENTIFIER,
    DOMAIN,
)


class AlbumsGeneratorConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for 1001 Albums Generator."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            group_slug = self._normalize_slug(
                user_input[CONF_GROUP_SLUG]
            )
            project_identifier = user_input[
                CONF_PROJECT_IDENTIFIER
            ].strip()

            if not group_slug:
                errors[CONF_GROUP_SLUG] = "invalid_group"

            elif not project_identifier:
                errors[CONF_PROJECT_IDENTIFIER] = (
                    "invalid_project"
                )

            else:
                await self.async_set_unique_id(
                    f"{group_slug}_{project_identifier.lower()}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME)
                    or project_identifier,
                    data={
                        CONF_NAME: user_input.get(CONF_NAME)
                        or project_identifier,
                        CONF_GROUP_SLUG: group_slug,
                        CONF_PROJECT_IDENTIFIER: project_identifier,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default="1001 Albums Generator",
                ): str,
                vol.Required(CONF_GROUP_SLUG): str,
                vol.Required(CONF_PROJECT_IDENTIFIER): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return AlbumsGeneratorOptionsFlow(config_entry)

    @staticmethod
    def _normalize_slug(value: str) -> str:
        """Convert a group name to an API slug."""
        return "-".join(value.strip().lower().split())


class AlbumsGeneratorOptionsFlow(
    config_entries.OptionsFlow,
):
    """Handle integration options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        schema = vol.Schema({})

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )