from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_PROJECT_IDENTIFIER,
    DOMAIN,
)


class AlbumsGeneratorConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for 1001 Albums Generator."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            project_identifier = user_input[
                CONF_PROJECT_IDENTIFIER
            ].strip()

            if not project_identifier:
                errors[
                    CONF_PROJECT_IDENTIFIER
                ] = "invalid_project"

            else:
                await self.async_set_unique_id(
                    project_identifier.lower()
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=project_identifier,
                    data={
                        CONF_PROJECT_IDENTIFIER: (
                            project_identifier
                        ),
                    },
                )

        schema = vol.Schema(
            {
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
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ):
        """Return the options flow."""
        return AlbumsGeneratorOptionsFlow()


class AlbumsGeneratorOptionsFlow(
    config_entries.OptionsFlow,
):
    """Handle integration options."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
        )