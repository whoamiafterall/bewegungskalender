import math

from nicegui import ui
from nicegui.elements.leaflet import Leaflet
from nicegui.elements.leaflet_layers import Marker
from slugify import slugify

from bewegungskalender.backend.formatting.format import event_time
from bewegungskalender.backend.io.config import MENU, MAP_CENTER_LAT, MAP_CENTER_LON, MAP_ZOOM, ASSETS_URL_PATH
from bewegungskalender.frontend.filter.controllers.location_filter_controller import LOCATION_FILTER
from bewegungskalender.frontend.filter.filter import events_using_filter
from bewegungskalender.frontend.filter.ui.category_filter import category_filters_ui
from bewegungskalender.frontend.filter.ui.location_filter import location_filter_ui
from bewegungskalender.frontend.filter.ui.time_filter import duration_filter_ui
from bewegungskalender.frontend.functions import loading
from bewegungskalender.frontend.navigation.router import ROUTER
from bewegungskalender.frontend.templates.templater import render_map_template
from bewegungskalender.libs.logger import LOGGER


# Create Map View
@ROUTER.add(f"/{slugify(str(MENU['map']['label'].lower()))}",True)
async def map_view():
    loading(MENU['map']['label'])
    await ui.context.client.connected()
    LOGGER.debug('Creating the Map to show events...')
    # new leaflet with center set to center of germany
    with ui.card().tight().classes('container mx-auto flex-row w-full sm:mt-55 max-sm:mb-[55px] p-0 m-0'):
        # force filter to use offline mode
        LOCATION_FILTER.location_type.force_offline = True
        @ui.refreshable
        async def create_map_ui():

            zoom = MAP_ZOOM
            center = (MAP_CENTER_LAT, MAP_CENTER_LON)
            if LOCATION_FILTER.location.result is not None:
                search_result = LOCATION_FILTER.location.result
                center = (search_result["lat"], search_result["lon"])

                # TODO: Find a more accurate way to figure out zoom level
                area = math.pow(LOCATION_FILTER.distance.value*3,2)

                zoom = math.floor(math.fabs(math.pow(area,1/8.5) - 12))


            leaflet = ui.leaflet(center=center, zoom=zoom).classes(
                'w-full h-[calc(100vh-55px)] p-0 m-0')

            with leaflet:

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
                if LOCATION_FILTER.location.result is not None:
                    leaflet.generic_layer(name='circle', args=[center, {'color': 'grey','opacity': 0.02, 'radius': LOCATION_FILTER.distance.value*1000}])

                # get cached data
                events = events_using_filter()

                LOGGER.info(f"Got {events.__len__()} locations to display...")

                # wait for leaflet to be initialized
                LOGGER.debug("Waiting for Leaflet to be initialized...")
                await leaflet.initialized()

                # loop trough Locations
                for event in events:
                    location = event.location
                    marker = leaflet.marker(latlng=(location.lat, location.lon))
                    LOGGER.debug(f"Created marker for {event.summary}.")

                    icon = (ASSETS_URL_PATH + '/icons/' + event.category.map_marker)

                    # set icon (don't run with await, that causes issues for some reason ...)
                    marker.run_method(':setIcon', f"L.icon({{iconUrl: '{icon}',iconSize: [40,40],iconAnchor:[20, 40],popupAnchor:[0,-40]}})")

                    # use template html file and replace variables TODO: use a proper templating language like Jinja? (Didn't want to setup a templating environment just for one file though)
                    # it might also a be an option to be generate all the html popups and store them as properties themselves also.
                    context = {"summary": event.summary, "event_time": event_time(event.start, event.end), "location": location.name, "link": event.location.osm_link}
                    bind_popup(leaflet, marker, context)

        await create_map_ui()


        # Filter
        with ui.column(wrap=False, align_items='start').classes(
                'm-0 gap-1 px-5 max-w-1/4 pt-5 shrink text-sm max-lg:hidden'):
            duration_filter_ui()
            location_filter_ui()
            await category_filters_ui()

        ui.on('refresh_filter', lambda: create_map_ui.refresh(), throttle=0.5, leading_events=False)

def bind_popup(leaflet:Leaflet, marker:Marker, context:dict[str, str | None]):
    leaflet.run_layer_method(marker.id, 'bindPopup', render_map_template(context), timeout=5.0)