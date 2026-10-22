from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME

from .const import (
    CONF_GROUP_SLUG,
    CONF_PROJECT_IDENTIFIER,
    DOMAIN,
)


def normalize_group(value: str) -> str:
    """Normalize a group name to a slug."""
    return "-".join(value.strip().lower().split())


def build_schema(current: dict[str, Any]) -> vol.Schema:
    """Build the setup and reconfiguration form."""
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME,
                default=current.get(
                    CONF_NAME,
                    "1001 Albums Generator",
                ),
            ): str,
            vol.Required(
                CONF_PROJECT_IDENTIFIER,
                default=current.get(
                    CONF_PROJECT_IDENTIFIER,
                    "",
                ),
            ): str,
            vol.Optional(
                CONF_GROUP_SLUG,
                default=current.get(CONF_GROUP_SLUG, ""),
            ): str,
        }
    )


class AlbumsGeneratorConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Configure 1001 Albums Generator."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle initial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            project = user_input[
                CONF_PROJECT_IDENTIFIER
            ].strip()

            if not project:
                errors[
                    CONF_PROJECT_IDENTIFIER
                ] = "invalid_project"
            else:
                # Preserve the identifier's spelling and case.
                await self.async_set_unique_id(
                    f"project:{project}"
                )
                self._abort_if_unique_id_configured()

                name = (
                    user_input.get(CONF_NAME, "").strip()
                    or project
                )

                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_PROJECT_IDENTIFIER: project,
                        CONF_GROUP_SLUG: normalize_group(
                            user_input.get(
                                CONF_GROUP_SLUG,
                                "",
                            )
                        ),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=build_schema(user_input or {}),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Update the group without removing the integration."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            project = user_input[
                CONF_PROJECT_IDENTIFIER
            ].strip()

            if not project:
                errors[
                    CONF_PROJECT_IDENTIFIER
                ] = "invalid_project"
            elif project != entry.data[
                CONF_PROJECT_IDENTIFIER
            ]:
                errors[
                    CONF_PROJECT_IDENTIFIER
                ] = "project_change_not_allowed"
            else:
                name = (
                    user_input.get(CONF_NAME, "").strip()
                    or project
                )

                return self.async_update_reload_and_abort(
                    entry,
                    title=name,
                    data_updates={
                        CONF_NAME: name,
                        CONF_GROUP_SLUG: normalize_group(
                            user_input.get(
                                CONF_GROUP_SLUG,
                                "",
                            )
                        ),
                    },
                )

        current = dict(entry.data)
        if user_input is not None:
            current.update(user_input)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=build_schema(current),
            errors=errors,
        )