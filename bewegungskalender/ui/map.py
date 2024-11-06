from nicegui import ui
from bewegungskalender.output.map import read_mapdata
from bewegungskalender.ui.templater import render_map_template

async def configure_map(leaflet:ui.leaflet):
    leaflet.clear_layers()

    # add ui on bottom right for copyright and set leaflet template(the style) + zoom
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
            
    return leaflet