from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    API_BASE_URL,
    API_WRITE_BASE_URL,
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
                project_data = await self._get_json(
                    session,
                    project_url,
                )
                albums_data = await self._get_json(
                    session,
                    albums_url,
                )
            data = {
                "project": project_data,
                "albums": self._extract_album_list(albums_data),
                "raw_albums": albums_data,
            }

            _LOGGER.debug(
                "1001 Albums Generator data received: %s",
                {
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

    async def async_rate_latest_album(
        self,
        rating: int,
        notes: str = "",
    ) -> None:
        """Submit a rating for the latest generated album."""
        history_item = get_latest_history_item(
            self.data.get("project", {})
        )
        if history_item is None:
            raise HomeAssistantError(
                "There is no generated album available to rate."
            )

        album = history_item.get("album", history_item)
        if not isinstance(album, dict):
            raise HomeAssistantError(
                "The latest history item has no album data."
            )

        album_id = album.get("uuid") or album.get("id")
        generated_album_id = (
            history_item.get("generatedAlbumId")
            or history_item.get("_id")
        )
        if not isinstance(album_id, str) or not isinstance(
            generated_album_id,
            str,
        ):
            raise HomeAssistantError(
                "The latest history item is missing rating IDs."
            )

        url = (
            f"{API_WRITE_BASE_URL}/"
            f"{quote(self.project_identifier, safe='')}/"
            f"{quote(album_id, safe='')}/rate"
        )
        payload = {
            "rating": rating,
            "notes": notes,
            "fromHistoryView": True,
            "generatedAlbumId": generated_album_id,
            "isUserAlbum": history_item.get("isUserAlbum", False)
            is True,
        }

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                async with session.post(
                    url,
                    json=payload,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": (
                            "Home Assistant 1001 Albums "
                            "Generator integration"
                        ),
                    },
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

            if not isinstance(result, dict):
                raise HomeAssistantError(
                    "The rating response had an unexpected format."
                )
            if result.get("success") is False or result.get("error"):
                raise HomeAssistantError(
                    "1001 Albums Generator rejected the rating: "
                    f"{result.get('error', 'unknown error')}"
                )

        except aiohttp.ClientResponseError as error:
            raise HomeAssistantError(
                f"Rating request failed with HTTP {error.status}."
            ) from error
        except aiohttp.ClientError as error:
            raise HomeAssistantError(
                f"Could not send the rating: {error}"
            ) from error
        except TimeoutError as error:
            raise HomeAssistantError(
                "The rating request timed out."
            ) from error
        except ValueError as error:
            raise HomeAssistantError(
                "The rating response was not valid JSON."
            ) from error

        await self.async_request_refresh()

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


def get_latest_history_item(
    project: dict[str, Any],
) -> dict[str, Any] | None:
    """Return the latest generated album with the IDs needed to rate it."""
    history = project.get("history")
    if not isinstance(history, list):
        return None

    for item in reversed(history):
        if not isinstance(item, dict):
            continue

        album = item.get("album", item)
        if not isinstance(album, dict):
            continue

        album_id = album.get("uuid") or album.get("id")
        generated_album_id = (
            item.get("generatedAlbumId") or item.get("_id")
        )
        if isinstance(album_id, str) and isinstance(
            generated_album_id,
            str,
        ):
            return item

    return None