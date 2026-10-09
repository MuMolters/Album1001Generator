# 1001 Albums Generator for Home Assistant

Integration to show your 1001 Albums Generator stats in Home Assistant.

## Installation

1. Install via HACS
2. Search for 1001 Albums Generator
3. Click Install
4. Restart Home Assistant
5. Add integration via Settings → Devices & Services

## Configuration

Enter the project name or sharer ID. A group slug is not required.

## Dashboard cards

The current album sensor provides `image_url` and `spotify_url` attributes and
uses the cover as its entity picture. With the [button-card](https://github.com/custom-cards/button-card)
custom card, you can show the cover and open that album on Spotify:

```yaml
type: custom:button-card
entity: sensor.huidig_album
show_entity_picture: true
show_name: false
show_state: true
tap_action:
  action: url
  url_path: |
    [[[ return entity.attributes.spotify_url; ]]]
```

Replace `sensor.huidig_album` with the entity ID created by Home Assistant.

### Rate yesterday's album from Home Assistant

The `sensor.album_om_te_beoordelen` entity shows the latest generated album in
your project history (normally yesterday's album). Add five buttons to rate it
from 1 to 5:

```yaml
type: horizontal-stack
cards:
  - type: custom:button-card
    entity: sensor.album_om_te_beoordelen
    name: "1"
    show_state: false
    tap_action:
      action: call-service
      service: albums_generator.rate_album
      service_data:
        project_identifier: '[[[ return entity.attributes.project_identifier; ]]]'
        rating: 1
  - type: custom:button-card
    entity: sensor.album_om_te_beoordelen
    name: "2"
    show_state: false
    tap_action:
      action: call-service
      service: albums_generator.rate_album
      service_data:
        project_identifier: '[[[ return entity.attributes.project_identifier; ]]]'
        rating: 2
  - type: custom:button-card
    entity: sensor.album_om_te_beoordelen
    name: "3"
    show_state: false
    tap_action:
      action: call-service
      service: albums_generator.rate_album
      service_data:
        project_identifier: '[[[ return entity.attributes.project_identifier; ]]]'
        rating: 3
  - type: custom:button-card
    entity: sensor.album_om_te_beoordelen
    name: "4"
    show_state: false
    tap_action:
      action: call-service
      service: albums_generator.rate_album
      service_data:
        project_identifier: '[[[ return entity.attributes.project_identifier; ]]]'
        rating: 4
  - type: custom:button-card
    entity: sensor.album_om_te_beoordelen
    name: "5"
    show_state: false
    tap_action:
      action: call-service
      service: albums_generator.rate_album
      service_data:
        project_identifier: '[[[ return entity.attributes.project_identifier; ]]]'
        rating: 5
```

Each button submits a rating for the latest generated album in the selected
project's history. The action refreshes the integration after the website
accepts the rating. You can also call `albums_generator.rate_album` from
Developer Tools → Actions, supplying the project identifier, a rating from 1
to 5, and optional review text.

The favorite and least-favorite sensors rank only albums in this project's
history that have a personal rating. Their full rated lists are in the
`albums` attribute. To display the list, you can use Markdown cards:

```yaml
type: markdown
content: |
  ## Favorite albums
  {% for album in state_attr('sensor.favoriete_albums', 'albums') or [] %}
  - **{{ album.album_title }}** — {{ album.artist }} ({{ album.rating }})
  {% endfor %}
```

Use `sensor.minst_favoriete_albums` and change the heading to show the
least-favorite albums. Replace the example entity IDs with the IDs in your
Home Assistant instance.