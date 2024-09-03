import os
import json
from nicegui import ui
from bewegungskalender.helper.config import config
from bewegungskalender.helper.formatting import italic, Format

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
   
    #itirate through map data dir and get all .geojson files (each being a collection of features)
    #note: the current implenetation is built around the original /data dir and how umap.py populates it. It might be reasonable to rework umap.py and /data functionality to better suit leaflet.
    for file in os.listdir(config['datadir']):
        
        if file.endswith(".geojson"):
            #get file name without .gejson ending
            filename:str = file[:-len(".geojson")]
            #set icon path based on filename which is unique to each map feature collection
            icon = 'assets/icons/' + filename + '.svg'

            # open file
            with open(config['datadir'] + "/" + filename + ".geojson", 'r') as f:
                #read as json
                file_data = json.load(f)

                #loop trough features
                for feature in file_data["features"]:

                    #add them as markers
                    lat = feature["geometry"]["coordinates"][1]
                    lng = feature["geometry"]["coordinates"][0]
                    marker = map.marker(latlng=(lat, lng))

                    #set icon (icon path was defined earlier based on feature collection file name)
                    marker.run_method(':setIcon', f"L.icon({{iconUrl: '{icon}',iconSize: [30,30],iconAnchor:[15, 30],popupAnchor:[0,-30]}})")
                                
                    # make a popup html string to pass to map
                    popuphtml = ""
                    for key in feature["properties"]:
                        value = feature["properties"][key]
                        #handle links (it might be good to )
                        popuphtml = popuphtml + f"{(key)} {value}<br>"
                   # popuphtml = popuphtml + f"<br> {italic(filename.replace("_", " "), Format.HTML)}"

                    ## pass popup html to  map and bind to marker id
                    map.run_layer_method(marker.id, 'bindPopup', popuphtml)
    return map