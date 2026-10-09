from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    API_BASE_URL,
    CONF_GROUP_SLUG,
    CONF_PROJECT_IDENTIFIER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class AlbumsGeneratorCoordinator(
    DataUpdateCoordinator[dict[str, Any]]
):
    """Fetch data from the 1001 Albums Generator API."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        self.entry = entry
        self.group_slug = entry.data[CONF_GROUP_SLUG]
        self.project_identifier = entry.data[
            CONF_PROJECT_IDENTIFIER
        ]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all API data."""
        group_url = (
            f"{API_BASE_URL}/groups/{self.group_slug}"
        )
        project_url = (
            f"{API_BASE_URL}/projects/"
            f"{self.project_identifier}"
        )
        albums_url = f"{API_BASE_URL}/albums/stats"

        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:
                group_data = await self._get_json(
                    session,
                    group_url,
                )
                project_data = await self._get_json(
                    session,
                    project_url,
                )
                albums_data = await self._get_json(
                    session,
                    albums_url,
                )

            data = {
                "group": group_data,
                "project": project_data,
                "albums": self._extract_album_list(albums_data),
                "raw_albums": albums_data,
            }

            _LOGGER.debug(
                "1001 Albums Generator data received: %s",
                {
                    "group_type": type(group_data).__name__,
                    "project_type": type(project_data).__name__,
                    "album_count": len(data["albums"]),
                },
            )

            return data

        except aiohttp.ClientResponseError as error:
            raise UpdateFailed(
                f"API returned HTTP {error.status}"
            ) from error

        except aiohttp.ClientError as error:
            raise UpdateFailed(
                f"Connection to API failed: {error}"
            ) from error

        except TimeoutError as error:
            raise UpdateFailed(
                "Connection to API timed out"
            ) from error

        except ValueError as error:
            raise UpdateFailed(
                f"Invalid JSON received from API: {error}"
            ) from error

    @staticmethod
    async def _get_json(
        session: aiohttp.ClientSession,
        url: str,
    ) -> Any:
        """Get JSON from an endpoint."""
        async with session.get(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": (
                    "Home Assistant 1001 Albums "
                    "Generator integration"
                ),
            },
        ) as response:
            response.raise_for_status()
            return await response.json()

    @staticmethod
    def _extract_album_list(data: Any) -> list[dict[str, Any]]:
        """Extract the album list from different response shapes."""
        if isinstance(data, list):
            return [
                item for item in data
                if isinstance(item, dict)
            ]

        if not isinstance(data, dict):
            return []

        possible_keys = (
            "albums",
            "albumStats",
            "album_stats",
            "results",
            "data",
        )

        for key in possible_keys:
            value = data.get(key)

            if isinstance(value, list):
                return [
                    item for item in value
                    if isinstance(item, dict)
                ]

            if isinstance(value, dict):
                nested = AlbumsGeneratorCoordinator
                return nested._extract_album_list(value)

        for value in data.values():
            if isinstance(value, list):
                dict_items = [
                    item for item in value
                    if isinstance(item, dict)
                ]

                if dict_items:
                    return dict_items

        return []