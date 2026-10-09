from __future__ import annotations

from datetime import timedelta

DOMAIN = "albums_generator"

CONF_GROUP_SLUG = "group_slug"
CONF_PROJECT_IDENTIFIER = "project_identifier"

DEFAULT_SCAN_INTERVAL = timedelta(hours=1)

API_BASE_URL = "https://1001albumsgenerator.com/api/v1"

ATTR_ALBUMS = "albums"
ATTR_ARTIST = "artist"
ATTR_ALBUM_TITLE = "album_title"
ATTR_YEAR = "year"
ATTR_GENRE = "genre"
ATTR_RATING = "rating"
ATTR_AVERAGE_RATING = "average_rating"
ATTR_SPOTIFY_URL = "spotify_url"
ATTR_IMAGE_URL = "image_url"
ATTR_VOTES = "votes"
ATTR_DECADE = "decade"
ATTR_CONTROVERSY = "controversy"
ATTR_PROJECT = "project"
ATTR_GROUP = "group"

SENSOR_TOTAL_ALBUMS = "total_albums"
SENSOR_COMPLETED_ALBUMS = "completed_albums"
SENSOR_REMAINING_ALBUMS = "remaining_albums"
SENSOR_COMPLETION_PERCENTAGE = "completion_percentage"
SENSOR_AVERAGE_RATING = "average_rating"
SENSOR_CURRENT_ALBUM = "current_album"
SENSOR_FAVORITE_ALBUMS = "favorite_albums"
SENSOR_LEAST_FAVORITE_ALBUMS = "least_favorite_albums"
SENSOR_GENRES = "genres"
SENSOR_DECADES = "decades"
SENSOR_CONTROVERSIAL_ALBUMS = "controversial_albums"