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

### Choose and rate any unrated album from Home Assistant

The `select.1001_albums_generator_album_om_te_beoordelen` entity lists albums
in your project history that do not have a personal rating. Add it to an
Entities card so you can choose which album to rate, then add five buttons to
submit a rating from 1 to 5:

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: select.1001_albums_generator_album_om_te_beoordelen
  - type: horizontal-stack
    cards:
      - type: custom:button-card
        entity: select.1001_albums_generator_album_om_te_beoordelen
        name: "1"
        show_state: false
        tap_action:
          action: call-service
          service: albums_generator.rate_album
          service_data:
            select_entity_id: select.1001_albums_generator_album_om_te_beoordelen
            rating: 1
      - type: custom:button-card
        entity: select.1001_albums_generator_album_om_te_beoordelen
        name: "2"
        show_state: false
        tap_action:
          action: call-service
          service: albums_generator.rate_album
          service_data:
            select_entity_id: select.1001_albums_generator_album_om_te_beoordelen
            rating: 2
      - type: custom:button-card
        entity: select.1001_albums_generator_album_om_te_beoordelen
        name: "3"
        show_state: false
        tap_action:
          action: call-service
          service: albums_generator.rate_album
          service_data:
            select_entity_id: select.1001_albums_generator_album_om_te_beoordelen
            rating: 3
      - type: custom:button-card
        entity: select.1001_albums_generator_album_om_te_beoordelen
        name: "4"
        show_state: false
        tap_action:
          action: call-service
          service: albums_generator.rate_album
          service_data:
            select_entity_id: select.1001_albums_generator_album_om_te_beoordelen
            rating: 4
      - type: custom:button-card
        entity: select.1001_albums_generator_album_om_te_beoordelen
        name: "5"
        show_state: false
        tap_action:
          action: call-service
          service: albums_generator.rate_album
          service_data:
            select_entity_id: select.1001_albums_generator_album_om_te_beoordelen
            rating: 5
```

Replace the select entity ID with the one shown in your Home Assistant entity
registry. The list refreshes with project data and the selected album
disappears after it is rated. The action also accepts optional review text.
The rating buttons pass the selector entity ID so the action reads its current
selection and project directly; this avoids relying on a card to template
dynamic service data. You can also call `albums_generator.rate_album` from
Developer Tools → Actions by providing the project identifier, a rating from
1 to 5, and either the generated album ID or the selector entity ID, plus
optional review text. The selector entity ID alone supplies the project.

The selected album's Spotify URL is available as the select entity's
`spotify_url` attribute. To make a button-card open that album when tapped:

```yaml
type: custom:button-card
entity: select.1001_albums_generator_album_om_te_beoordelen
show_state: true
tap_action:
  action: url
  url_path: |
    [[[ return entity.attributes.spotify_url; ]]]
```

The `Favoriete albums` and `Minst favoriete albums` sensors list albums
personally rated in this project. `Best beoordeelde albums` and
`Slechtst beoordeelde albums` are the overall site rankings. Genre sensors
have been removed. The project favorite sensors' full lists are in the
`albums` attribute. To display one with a Markdown card:

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