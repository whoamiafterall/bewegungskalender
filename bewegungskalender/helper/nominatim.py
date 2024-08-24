import json
import logging
import re
import urllib3

#TODO: Refactor to have one Main class and override methods

class NominatimSearch(object):
    """Class for querying text adress
    https://nominatim.org/release-docs/develop/api/Search/"""
    def __init__(self):
        self.url = 'https://nominatim.openstreetmap.org/search?format=json'
        self.logger = logging.getLogger(__name__)

    def query(self, query, acceptlanguage='', limit=None):
        """Method takes query string, acceptlanguage string (rfc2616 language 
code), limit integer (limits number of results)."""
        query = query.replace(' ', '+')
        url = self.url + '&q=' + query
        if acceptlanguage:
            url += '&accept-language=' + acceptlanguage
        if limit:
            url += '&limit=' + str(limit)
        self.logger.debug('url:\n' + url)
        result = urllib3.request('GET',url).data
        return json.loads(result) if result != "" else None
           

class NominatimReverse(object):
    """Class for querying gps coordinates
    https://nominatim.org/release-docs/develop/api/Reverse/
"""
    def __init__(self):
        self.url = 'https://nominatim.openstreetmap.org/reverse?format=json'
        self.logger = logging.getLogger(__name__)

    def query(self, lat=None, lon=None, acceptlanguage='', zoom=18):
        """Method takes lat and lon for GPS coordinates, acceptlanguage string,
zoom integer (between from 0 to 18). """
        url = self.url
        if lat and lon:
            url += '&lat=' + str(lat) + '&lon=' + str(lon)
        if acceptlanguage:
            url += '&accept-language=' + acceptlanguage
        if zoom < 0 or zoom > 18:
            raise Exception('zoom must be betwen 0 and 18')
        url +='&zoom=' + str(zoom)
        self.logger.debug('url:\n' + url)
        result = urllib3.request('GET',url).data
        return json.loads(result) if result != "" else None
          

class NominatimLookup(object):
    """Class for querying Ways, Nodes, etc. (Osm-IDs)
https://nominatim.org/release-docs/develop/api/Lookup/"""
    def __init__(self):
        self.url = 'https://nominatim.openstreetmap.org/lookup?format=json'
        self.logger = logging.getLogger(__name__)
        
    def query(self, query:str):
        """Method takes query string which must contain a comma-separated list of OSM ids each prefixed with its type, one of node(N), way(W) or relation(R)."""
        if query is None:
            return None
        if re.search('[NWR]\d{4,15}', query) is None:
            return None
        url = self.url
        url += '&osm_ids=' + query
        self.logger.debug('querying the following url:\n' + url)
        result = urllib3.request('GET',url).data
        return json.loads(result) if result != "" else None
