from __future__ import annotations

from datetime import timedelta

DOMAIN = "albums_generator"

CONF_PROJECT_IDENTIFIER = "project_identifier"
CONF_GROUP_SLUG = "group_slug"

DEFAULT_SCAN_INTERVAL = timedelta(hours=1)
DEFAULT_TOTAL_ALBUMS = 1089

API_BASE_URL = "https://1001albumsgenerator.com/api/v1"
API_WRITE_BASE_URL = "https://1001albumsgenerator.com/api"

SERVICE_RATE_ALBUM = "rate_album"

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

SENSOR_TOTAL_ALBUMS = "total_albums"
SENSOR_COMPLETED_ALBUMS = "completed_albums"
SENSOR_REMAINING_ALBUMS = "remaining_albums"
SENSOR_COMPLETION_PERCENTAGE = "completion_percentage"
SENSOR_AVERAGE_RATING = "average_rating"
SENSOR_CURRENT_ALBUM = "current_album"
SENSOR_FAVORITE_ALBUMS = "favorite_albums"
SENSOR_LEAST_FAVORITE_ALBUMS = "least_favorite_albums"
SENSOR_DECADES = "decades"
SENSOR_CONTROVERSIAL_ALBUMS = "controversial_albums"
SENSOR_TOP_RATED_ALBUMS = "top_rated_albums"
SENSOR_BOTTOM_RATED_ALBUMS = "bottom_rated_albums"

SENSOR_GROUP_STATS = "group_stats"

ATTR_GROUP_NAME = "group_name"
ATTR_GROUP_MEMBERS = "group_members"
ATTR_GROUP_AVERAGE_RATING = "group_average_rating"
ATTR_GROUP_TOTAL_VOTES = "group_total_votes"
ATTR_GROUP_COMPLETED_ALBUMS = "group_completed_albums"
ATTR_GROUP_CURRENT_ALBUM = "group_current_album"