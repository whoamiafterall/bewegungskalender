from nicegui import ui
from nicegui.elements.leaflet import Leaflet
from nicegui.elements.leaflet_layers import Marker
from slugify import slugify
from sqlmodel import select

from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.formatting.format import event_time
from bewegungskalender.backend.io import db
from bewegungskalender.backend.io.config import MENU, MAP_CENTER_LAT, MAP_CENTER_LON, MAP_ZOOM
from bewegungskalender.frontend.functions import loading
from bewegungskalender.frontend.navigation.router import ROUTER
from bewegungskalender.frontend.templater import render_map_template
from bewegungskalender.libs.logger import LOGGER


# Create Map View
@ROUTER.add(f"/{slugify(str(MENU['map']['label'].lower()))}")
async def map_view():
    loading(MENU['map']['label'])
    await ui.context.client.connected()
    LOGGER.debug('Creating the Map to show events...')
    # new leaflet with center set to center of germany
    with ui.leaflet(center=(MAP_CENTER_LAT, MAP_CENTER_LON), zoom=MAP_ZOOM).classes('w-full h-full') as leaflet:
        with ui.page_sticky(x_offset=18, y_offset=18).classes(
                'sm:hidden z-5000'):  # TODO Fix (it's not shown for whatever reason)
            ui.button(icon='filter_alt', #on_click=lambda: right_drawer.toggle()
                       ).props('fab color=accent')
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

        # get cached data
        locations:list[Location] = db.exe(select(Location).where(Location.lat is not None)).all()
        LOGGER.info(f"Got {locations.__len__()} to display...")

        # wait for leaflet to be initialized
        LOGGER.debug("Waiting for Leaflet to be initialized...")
        await leaflet.initialized()

        # loop trough Locations
        for location in locations:
            marker = leaflet.marker(latlng=(location.lat, location.lon))
            LOGGER.info(f"Created marker for {location.event.summary}.")

            # set icon
            await marker.run_method(':setIcon', f"L.icon({{iconUrl: '{location.event.category.map_marker}',iconSize: [60,60],iconAnchor:[30, 60],popupAnchor:[0,-60]}})")

            # use template html file and replace variables TODO: use a proper templating language like Jinja? (Didn't want to setup a templating environment just for one file though)
            # it might also a be an option to be generate all the html popups and store them as properties themselves also.
            context = {"summary": location.event.summary, "event_time": event_time(location.event.start, location.event.end), "location": location.name, "link": location.event.link}
            bind_popup(leaflet, marker, context)

def bind_popup(leaflet:Leaflet, marker:Marker, context:dict[str, str | None]):
    leaflet.run_layer_method(marker.id, 'bindPopup', render_map_template(context), timeout=5.0)