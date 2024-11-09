from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.io.config import MAIN_MENU, MAP_CENTER_LAT, MAP_CENTER_LON, MAP_ZOOM
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.backend.output.map_data import read_mapdata
from bewegungskalender.frontend.functions import loading
from bewegungskalender.frontend.navigation.router import ROUTER
from bewegungskalender.frontend.templater import render_map_template

# Create Map View
@ROUTER.add(slugify(f"/{str(MAIN_MENU['map']['label'].lower())}"))
async def map_view(right_drawer):
    loading(MAIN_MENU['map']['label'])
    LOGGER.debug('Creating the Map to show events...')
    # new leaflet with center set to center of germany
    with ui.leaflet(center=(MAP_CENTER_LAT, MAP_CENTER_LON), zoom=MAP_ZOOM).classes('w-full h-full') as leaflet:
        with ui.page_sticky(x_offset=18, y_offset=18).classes(
                'sm:hidden z-5000'):  # TODO Fix (it's not shown for whatever reason)
            ui.button(icon='filter_alt', on_click=lambda: right_drawer.toggle()).props(
                'fab color=accent')
        leaflet.clear_layers()

        # add frontend on bottom right for copyright and set leaflet template(the style) + zoom
        leaflet.tile_layer(

            url_template=r'https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
            options={
                'minZoom': 3,
                'maxZoom': 16,
                'attribution':
                    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://viewfinderpanoramas.org/">SRTM</a> | '
                    '&copy; <a href="https://carto.com">Carto</a>'
            },
        )

        # wait for leaflet to be intialized
        await leaflet.initialized()

        # get cached data
        featureCollections:list = read_mapdata()

        #loop trough feature collections
        for featureCollection in featureCollections:
            #loop trough features
            for feature in featureCollection["features"]:
                lat = feature["geometry"]["coordinates"][1]
                lng = feature["geometry"]["coordinates"][0]
                marker = leaflet.marker(latlng=(lat, lng))

                #set icon
                await marker.run_method(':setIcon', f"L.icon({{iconUrl: '{featureCollection['map_marker']}',iconSize: [60,60],iconAnchor:[30, 60],popupAnchor:[0,-60]}})")

                #use template html file and replace variables TODO: use a proper templating language like Jinja? (Didn't want to setup a templating environment just for one file though)
                #it might also a be an option to be generate all the html popups and store them as properties themselves also.
                properties = feature["properties"]
                context = {"summary": properties["summary"],"event_time": properties["event_time"],"location": properties["location"],"link": properties["link"]}
                await leaflet.run_layer_method(marker.id, 'bindPopup', render_map_template(context))