from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import (
    AlbumsGeneratorCoordinator,
    get_unrated_history_items,
)
from .sensor import (
    get_album_title,
    get_artist,
    get_image_url,
    get_spotify_url,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the unrated-album selector."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([UnratedAlbumSelect(coordinator)])


class UnratedAlbumSelect(
    CoordinatorEntity[AlbumsGeneratorCoordinator],
    SelectEntity,
):
    """Choose a generated project album that has not been rated."""

    _attr_has_entity_name = True
    _attr_name = "Album om te beoordelen"
    _attr_icon = "mdi:playlist-music"

    def __init__(
        self,
        coordinator: AlbumsGeneratorCoordinator,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{DOMAIN}_{coordinator.entry.entry_id}_"
            "unrated_album"
        )
        self._attr_options: list[str] = []
        self._attr_current_option: str | None = None
        self._options_by_id: dict[str, dict[str, Any]] = {}
        self._ids_by_option: dict[str, str] = {}
        self._refresh_options()

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {
                (DOMAIN, self.coordinator.entry.entry_id)
            },
            "name": "1001 Albums Generator",
            "manufacturer": "1001 Albums Generator",
            "model": "API",
        }

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose selected album details for rating buttons."""
        item = self._options_by_id.get(
            self._ids_by_option.get(
                self._attr_current_option or "",
                "",
            ),
            {},
        )
        if not item:
            return {
                "project_identifier": self.coordinator.project_identifier,
                "generated_album_id": "",
            }

        album = item.get("album", item)
        if not isinstance(album, dict):
            album = {}

        return {
            "project_identifier": (
                self.coordinator.project_identifier
            ),
            "generated_album_id": (
                item.get("generatedAlbumId") or item.get("_id")
            ),
            "album_id": album.get("uuid") or album.get("id"),
            "image_url": get_image_url(album),
            "spotify_url": get_spotify_url(album),
        }

    async def async_select_option(self, option: str) -> None:
        """Select an unrated project album."""
        if option not in self._ids_by_option:
            raise HomeAssistantError(
                "That album is no longer available to rate."
            )

        self._attr_current_option = option
        self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Refresh options when project history changes."""
        self._refresh_options()
        super()._handle_coordinator_update()

    def _refresh_options(self) -> None:
        """Build unique readable options from unrated history."""
        selected_id = self._ids_by_option.get(
            self._attr_current_option or ""
        )
        options_by_id: dict[str, dict[str, Any]] = {}
        ids_by_option: dict[str, str] = {}

        for item in get_unrated_history_items(
            self.coordinator.data.get("project", {})
        ):
            generated_id = (
                item.get("generatedAlbumId") or item.get("_id")
            )
            if not isinstance(generated_id, str):
                continue

            album = item.get("album", item)
            if not isinstance(album, dict):
                continue

            title = get_album_title(album) or "Unknown album"
            artist = get_artist(album)
            label = f"{title} — {artist}" if artist else title
            base_label = label
            id_prefix_length = 6
            while label in ids_by_option:
                label = (
                    f"{base_label} "
                    f"[{generated_id[:id_prefix_length]}]"
                )
                id_prefix_length += 2

            options_by_id[generated_id] = item
            ids_by_option[label] = generated_id

        self._options_by_id = options_by_id
        self._ids_by_option = ids_by_option
        self._attr_options = list(ids_by_option)

        if selected_id is None:
            self._attr_current_option = None
        else:
            self._attr_current_option = next(
                (
                    label
                    for label, item_id in ids_by_option.items()
                    if item_id == selected_id
                ),
                None,
            )
