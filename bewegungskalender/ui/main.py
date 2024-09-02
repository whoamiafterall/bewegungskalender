import os
import json
from nicegui import ui,app
from bewegungskalender.helper.config import config
from bewegungskalender.helper.formatting import italic,Format

from geojson import Feature, FeatureCollection
from pathlib import Path

#for the time being the map can be accessed using a subpage called /map, this can and maybe shoud be changed
@ui.page('/map')
async def map_page():

    # new map with center set to center of germany
    m = ui.leaflet(center=(51.165691, 10.451526), zoom=4)
    m.clear_layers()

    # add ui on bottom right for copyright and set map template(the style) + zoom
    m.tile_layer(

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
    await m.initialized()
   
    #itirate through map data dir and get all .geojson files (each being a collection of features)
    #note: the current implenetation is built around the original /data dir and how umap.py populates it. It might be reasonable to rework umap.py and /data functionality to better suit leaflet.
    for x in os.listdir(config['datadir']):
        
        if x.endswith(".geojson"):
            #get file name without .gejson ending
            c = x[:-len(".geojson")]
            #set icon path based on filename which is unique to each map feature collection
            icon = 'assets/icons/'+c+'.svg'

            # open file
            with open(config['datadir']+"/"+x, 'r') as f:
                #read as json
                frie_data = json.load(f)

                #loop trough features
                for feature in frie_data["features"]:

                    #add them as markers
                    lat = feature["geometry"]["coordinates"][1]
                    lng = feature["geometry"]["coordinates"][0]
                    marker = m.marker(latlng=(lat, lng))

                    #set icon (icon path was defined earlier based on feature collection file name)
                    marker.run_method(':setIcon', 'L.icon({iconUrl: "'+icon+'",iconSize: [20,20],iconAnchor:[10, 10]})')
                                
                    # make a popup html string to pass to map
                    popuphtml = ""
                    for key in feature["properties"]:
                        value = feature["properties"][key]
                        #handle links (it might be good to )
                        popuphtml = popuphtml + f"{(key)} {value}<br>"
                    popuphtml = popuphtml + f"<br> {italic(c.replace("_"," "),Format.HTML)}"

                    ## pass popup html to  map and bind to marker id
                    m.run_layer_method(marker.id, 'bindPopup', popuphtml)

                
    


def start_ui():       
    #add statis files
    app.add_static_files("/assets", "bewegungskalender/ui/assets")      
    #run map
    ui.run()


