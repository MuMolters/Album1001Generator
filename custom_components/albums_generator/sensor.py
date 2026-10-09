from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    ATTR_ALBUMS,
    ATTR_ALBUM_TITLE,
    ATTR_ARTIST,
    ATTR_AVERAGE_RATING,
    ATTR_CONTROVERSY,
    ATTR_DECADE,
    ATTR_GENRE,
    ATTR_GROUP,
    ATTR_IMAGE_URL,
    ATTR_PROJECT,
    ATTR_RATING,
    ATTR_SPOTIFY_URL,
    ATTR_VOTES,
    ATTR_YEAR,
    DOMAIN,
    SENSOR_AVERAGE_RATING,
    SENSOR_COMPLETED_ALBUMS,
    SENSOR_COMPLETION_PERCENTAGE,
    SENSOR_CONTROVERSIAL_ALBUMS,
    SENSOR_CURRENT_ALBUM,
    SENSOR_DECADES,
    SENSOR_FAVORITE_ALBUMS,
    SENSOR_GENRES,
    SENSOR_LEAST_FAVORITE_ALBUMS,
    SENSOR_REMAINING_ALBUMS,
    SENSOR_TOTAL_ALBUMS,
)
from .coordinator import AlbumsGeneratorCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        TotalAlbumsSensor(coordinator),
        CompletedAlbumsSensor(coordinator),
        RemainingAlbumsSensor(coordinator),
        CompletionPercentageSensor(coordinator),
        AverageRatingSensor(coordinator),
        CurrentAlbumSensor(coordinator),
        FavoriteAlbumsSensor(coordinator),
        LeastFavoriteAlbumsSensor(coordinator),
        GenresSensor(coordinator),
        DecadesSensor(coordinator),
        TopRatedAlbumsSensor(coordinator),
        BottomRatedAlbumsSensor(coordinator),
        GenreListSensor(coordinator),
    ]

    async_add_entities(entities)

class AlbumsGeneratorSensor(
    CoordinatorEntity[AlbumsGeneratorCoordinator],
    SensorEntity,
):
    """Base sensor for this integration."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AlbumsGeneratorCoordinator,
        sensor_key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)

        self._sensor_key = sensor_key
        self._attr_name = name
        self._attr_unique_id = (
            f"{DOMAIN}_{coordinator.entry.entry_id}_"
            f"{sensor_key}"
        )

    @property
    def device_info(self):
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
    def group_data(self) -> dict[str, Any]:
        """Return group data."""
        value = self.coordinator.data.get(ATTR_GROUP, {})
        return value if isinstance(value, dict) else {}

    @property
    def project_data(self) -> dict[str, Any]:
        """Return project data."""
        value = self.coordinator.data.get(ATTR_PROJECT, {})
        return value if isinstance(value, dict) else {}

    @property
    def albums(self) -> list[dict[str, Any]]:
        """Return album statistics."""
        value = self.coordinator.data.get(ATTR_ALBUMS, [])
        return value if isinstance(value, list) else []


class TotalAlbumsSensor(AlbumsGeneratorSensor):
    """Total number of albums."""

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_TOTAL_ALBUMS,
            "Totaal aantal albums",
        )

    @property
    def native_value(self):
        """Return total album count."""
        value = self._find_value(
            self.project_data,
            (
                "totalAlbums",
                "total_albums",
                "albumCount",
                "total",
            ),
        )

        if isinstance(value, (int, float)):
            return int(value)

        return 1001

    @staticmethod
    def _find_value(data, keys):
        for key in keys:
            if key in data:
                return data[key]

        return None


class CompletedAlbumsSensor(AlbumsGeneratorSensor):
    """Number of completed albums."""

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_COMPLETED_ALBUMS,
            "Beluisterde albums",
        )

    @property
    def native_value(self):
        """Return completed album count."""
        value = self._find_value(
            self.project_data,
            (
                "completedAlbums",
                "completed_albums",
                "ratedAlbums",
                "rated_albums",
                "generatedAlbums",
                "generated_albums",
            ),
        )

        if isinstance(value, (int, float)):
            return int(value)

        history = self._find_value(
            self.project_data,
            ("history", "albumHistory", "album_history"),
        )

        if isinstance(history, list):
            return len(history)

        return 0

    @staticmethod
    def _find_value(data, keys):
        for key in keys:
            if key in data:
                return data[key]

        return None


class RemainingAlbumsSensor(AlbumsGeneratorSensor):
    """Number of remaining albums."""

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_REMAINING_ALBUMS,
            "Albums te gaan",
        )

    @property
    def native_value(self):
        """Return remaining album count."""
        total = TotalAlbumsSensor._find_value(
            self.project_data,
            (
                "totalAlbums",
                "total_albums",
                "albumCount",
                "total",
            ),
        )

        completed = CompletedAlbumsSensor(
            self.coordinator
        ).native_value

        if not isinstance(total, (int, float)):
            total = 1001

        return max(int(total) - int(completed), 0)


class CompletionPercentageSensor(AlbumsGeneratorSensor):
    """Project completion percentage."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:progress-check"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_COMPLETION_PERCENTAGE,
            "Voortgang",
        )

    @property
    def native_value(self):
        """Return completion percentage."""
        total = TotalAlbumsSensor(
            self.coordinator
        ).native_value
        completed = CompletedAlbumsSensor(
            self.coordinator
        ).native_value

        if not total:
            return 0

        return round((completed / total) * 100, 1)


class AverageRatingSensor(AlbumsGeneratorSensor):
    """Average album rating."""

    _attr_icon = "mdi:star"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_AVERAGE_RATING,
            "Gemiddelde beoordeling",
        )

    @property
    def native_value(self):
        """Return average rating."""
        direct_value = self._find_value(
            self.project_data,
            (
                "averageRating",
                "average_rating",
                "averageScore",
                "average_score",
            ),
        )

        if isinstance(direct_value, (int, float)):
            return round(float(direct_value), 2)

        ratings = []

        for album in self.albums:
            rating = get_rating(album)

            if rating is not None:
                ratings.append(rating)

        if not ratings:
            return None

        return round(sum(ratings) / len(ratings), 2)

    @staticmethod
    def _find_value(data, keys):
        for key in keys:
            if key in data:
                return data[key]

        return None


class CurrentAlbumSensor(AlbumsGeneratorSensor):
    """Current album."""

    _attr_icon = "mdi:album"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_CURRENT_ALBUM,
            "Huidig album",
        )

    @property
    def native_value(self):
        """Return the current album title."""
        album = get_current_album(
            self.project_data,
            self.group_data,
        )

        return get_album_title(album) or "Onbekend album"

    @property
    def extra_state_attributes(self):
        """Return current album details."""
        album = get_current_album(
            self.project_data,
            self.group_data,
        )

        if not album:
            return {}

        return album_attributes(album)


class FavoriteAlbumsSensor(AlbumsGeneratorSensor):
    """Highest-rated albums."""

    _attr_icon = "mdi:heart"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_FAVORITE_ALBUMS,
            "Favoriete albums",
        )

    @property
    def native_value(self):
        """Return number of favorite albums."""
        return len(self.ranked_albums(reverse=True))

    @property
    def extra_state_attributes(self):
        """Return favorite album list."""
        return {
            ATTR_ALBUMS: [
                album_attributes(album)
                for album in self.ranked_albums(reverse=True)[:10]
            ]
        }

    def ranked_albums(self, reverse=False):
        return sorted(
            self.albums,
            key=lambda album: get_rating(album) or 0,
            reverse=reverse,
        )


class LeastFavoriteAlbumsSensor(AlbumsGeneratorSensor):
    """Lowest-rated albums."""

    _attr_icon = "mdi:thumb-down"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_LEAST_FAVORITE_ALBUMS,
            "Minst favoriete albums",
        )

    @property
    def native_value(self):
        """Return number of albums."""
        return len(self.albums)

    @property
    def extra_state_attributes(self):
        """Return least favorite album list."""
        albums = sorted(
            self.albums,
            key=lambda album: get_rating(album) or 999,
        )

        return {
            ATTR_ALBUMS: [
                album_attributes(album)
                for album in albums[:10]
            ]
        }


class GenresSensor(AlbumsGeneratorSensor):
    """Genre counts."""

    _attr_icon = "mdi:music-box-multiple"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_GENRES,
            "Genres",
        )

    @property
    def native_value(self):
        """Return number of detected genres."""
        return len(self.genre_counts())

    @property
    def extra_state_attributes(self):
        """Return genre counts."""
        return {
            "genre_counts": self.genre_counts()
        }

    def genre_counts(self):
        counts = {}

        for album in self.albums:
            genre = get_genre(album)

            if not genre:
                continue

            if isinstance(genre, list):
                genres = genre
            else:
                genres = [
                    item.strip()
                    for item in str(genre).split(",")
                    if item.strip()
                ]

            for item in genres:
                counts[item] = counts.get(item, 0) + 1

        return dict(
            sorted(
                counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )


class DecadesSensor(AlbumsGeneratorSensor):
    """Album counts per decade."""

    _attr_icon = "mdi:calendar-multiple"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_DECADES,
            "Decennia",
        )

    @property
    def native_value(self):
        """Return number of detected decades."""
        return len(self.decade_counts())

    @property
    def extra_state_attributes(self):
        """Return decade counts."""
        return {
            "decade_counts": self.decade_counts()
        }

    def decade_counts(self):
        counts = {}

        for album in self.albums:
            year = get_year(album)

            if year is None:
                continue

            decade = f"{(year // 10) * 10}s"
            counts[decade] = counts.get(decade, 0) + 1

        return dict(
            sorted(
                counts.items(),
                key=lambda item: item[0],
            )
        )


class TopRatedAlbumsSensor(AlbumsGeneratorSensor):
    """Top-rated albums list."""

    _attr_icon = "mdi:heart"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_TOP_RATED_ALBUMS,
            "Best beoordeelde albums",
        )

    @property
    def native_value(self):
        """Return number of top-rated albums."""
        return len(self.ranked_albums(reverse=True))

    @property
    def extra_state_attributes(self):
        """Return top-rated album list."""
        albums = self.ranked_albums(reverse=True)

        return {
            ATTR_ALBUMS: [
                album_attributes(album)
                for album in albums[:20]
            ]
        }

    def ranked_albums(self, reverse=False):
        return sorted(
            self.albums,
            key=lambda album: get_rating(album) or 0,
            reverse=reverse,
        )


class BottomRatedAlbumsSensor(AlbumsGeneratorSensor):
    """Lowest-rated albums list."""

    _attr_icon = "mdi:thumb-down"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_BOTTOM_RATED_ALBUMS,
            "Slechtst beoordeelde albums",
        )

    @property
    def native_value(self):
        """Return number of lowest-rated albums."""
        return len(self.ranked_albums())

    @property
    def extra_state_attributes(self):
        """Return lowest-rated album list."""
        albums = self.ranked_albums()

        return {
            ATTR_ALBUMS: [
                album_attributes(album)
                for album in albums[:20]
            ]
        }

    def ranked_albums(self, reverse=False):
        return sorted(
            self.albums,
            key=lambda album: get_rating(album) or 999,
            reverse=reverse,
        )


class GenreListSensor(AlbumsGeneratorSensor):
    """List of unique genres."""

    _attr_icon = "mdi:music-box-multiple"

    def __init__(self, coordinator):
        super().__init__(
            coordinator,
            SENSOR_GENRE_LIST,
            "Genres",
        )

    @property
    def native_value(self):
        """Return number of unique genres."""
        return len(self.unique_genres())

    @property
    def extra_state_attributes(self):
        """Return genre list."""
        return {
            "genres": self.unique_genres()
        }

    def unique_genres(self):
        genres_set = set()

        for album in self.albums:
            genre = get_genre(album)

            if not genre:
                continue

            if isinstance(genre, list):
                for item in genre:
                    if isinstance(item, str):
                        genres_set.add(item.strip())
            else:
                for item in str(genre).split(","):
                    if item.strip():
                        genres_set.add(item.strip())

        return sorted(list(genres_set))

def get_current_album(
    project: dict[str, Any],
    group: dict[str, Any],
) -> dict[str, Any]:
    """Find the current album."""
    for source in (project, group):
        for key in (
            "currentAlbum",
            "current_album",
            "albumOfTheDay",
            "album_of_the_day",
        ):
            value = source.get(key)

            if isinstance(value, dict):
                return value

    return {}


def get_album_title(album: dict[str, Any]) -> str | None:
    """Get an album title."""
    for key in (
        "title",
        "album",
        "name",
        "albumTitle",
        "album_title",
    ):
        value = album.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def get_artist(album: dict[str, Any]) -> str | None:
    """Get artist name."""
    for key in (
        "artist",
        "artistName",
        "artist_name",
        "artists",
    ):
        value = album.get(key)

        if isinstance(value, list):
            return ", ".join(str(item) for item in value)

        if value is not None:
            return str(value)

    return None


def get_year(album: dict[str, Any]) -> int | None:
    """Get release year."""
    for key in (
        "year",
        "releaseYear",
        "release_year",
        "date",
        "releaseDate",
        "release_date",
    ):
        value = album.get(key)

        if isinstance(value, int):
            return value

        if isinstance(value, str):
            digits = "".join(
                character
                for character in value
                if character.isdigit()
            )

            if len(digits) >= 4:
                return int(digits[:4])

    return None


def get_genre(album: dict[str, Any]) -> Any:
    """Get album genre."""
    for key in (
        "genre",
        "genres",
        "mainGenre",
        "main_genre",
    ):
        if key in album:
            return album[key]

    return None


def get_rating(album: dict[str, Any]) -> float | None:
    """Get rating from an album."""
    for key in (
        "averageScore",
        "average_score",
        "averageRating",
        "average_rating",
        "rating",
        "score",
    ):
        value = album.get(key)

        try:
            if value is not None:
                return float(value)
        except (TypeError, ValueError):
            continue

    return None


def get_votes(album: dict[str, Any]) -> int | None:
    """Get vote count."""
    for key in (
        "votes",
        "voteCount",
        "vote_count",
        "numberOfVotes",
        "number_of_votes",
    ):
        value = album.get(key)

        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            continue

    return None


def get_spotify_url(
    album: dict[str, Any],
) -> str | None:
    """Get Spotify URL."""
    for key in (
        "spotifyUrl",
        "spotify_url",
        "spotify",
    ):
        value = album.get(key)

        if isinstance(value, str) and value.startswith("http"):
            return value

    links = album.get("links")

    if isinstance(links, dict):
        value = links.get("spotify")

        if isinstance(value, str):
            return value

    return None


def get_image_url(
    album: dict[str, Any],
) -> str | None:
    """Get image URL."""
    for key in (
        "imageUrl",
        "image_url",
        "cover",
        "coverUrl",
        "cover_url",
        "artwork",
    ):
        value = album.get(key)

        if isinstance(value, str) and value.startswith("http"):
            return value

    return None


def get_controversy(
    album: dict[str, Any],
) -> float | None:
    """Get controversy or deviation value."""
    for key in (
        "controversialScore",
        "controversial_score",
        "controversy",
        "deviation",
        "standardDeviation",
        "standard_deviation",
    ):
        value = album.get(key)

        try:
            if value is not None:
                return float(value)
        except (TypeError, ValueError):
            continue

    return None


def album_attributes(
    album: dict[str, Any],
) -> dict[str, Any]:
    """Create clean album attributes."""
    values = {
        ATTR_ALBUM_TITLE: get_album_title(album),
        ATTR_ARTIST: get_artist(album),
        ATTR_YEAR: get_year(album),
        ATTR_GENRE: get_genre(album),
        ATTR_RATING: get_rating(album),
        ATTR_VOTES: get_votes(album),
        ATTR_SPOTIFY_URL: get_spotify_url(album),
        ATTR_IMAGE_URL: get_image_url(album),
        ATTR_CONTROVERSY: get_controversy(album),
    }

    return {
        key: value
        for key, value in values.items()
        if value is not None
    }