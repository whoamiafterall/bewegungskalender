import os
import json
from nicegui import ui
from bewegungskalender.helper.config import config
from bewegungskalender.helper.formatting import italic, Format
from geojson import Feature, FeatureCollection
from bewegungskalender.output.umap import readMapData


async def configure_map(map:ui.leaflet):
    map.clear_layers()
    # add ui on bottom right for copyright and set map template(the style) + zoom
    map.tile_layer(

        url_template=r'https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
        options={
            'minZoom': 3,
            'maxZoom': 16,
            'attribution':
                'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="https://viewfinderpanoramas.org/">SRTM</a> | '
                'Map style: &copy; <a href="https://carto.com">Carto</a>'
        },
    )

    #wait for map to be intialized
    await map.initialized()

    #call read data
    featureCollections:list = readMapData(config['mapdatadir'])
        
    #loop trough feature collections
    for featureCollection in featureCollections:
        #loop trough features
        for feature in featureCollection["features"]:
            lat = feature["geometry"]["coordinates"][1]
            lng = feature["geometry"]["coordinates"][0]
            marker = map.marker(latlng=(lat, lng))

            #set icon 
            marker.run_method(':setIcon', f"L.icon({{iconUrl: '{featureCollection['map_marker_url']}',iconSize: [30,30],iconAnchor:[15, 30],popupAnchor:[0,-30]}})")
                                             
            #use template html file and replace variables TODO: use a proper templating language like Jinja? (Didn't want to seutp a templating environment just for one file though)
            #it might also a be an option to be generate all the html popups and store them as properties themselves also.
            properties = feature["properties"]
            with open(config['map']['popup']['template_path'], 'r') as f:
                html:str = f.read().format(summary=properties["summary"],eventtime=properties["eventtime"],location=properties["location"],link=properties["link"])
                map.run_layer_method(marker.id, 'bindPopup', html)
            
    return map