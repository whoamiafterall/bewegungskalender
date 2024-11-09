import json
import re
from logging import Logger, getLogger
import urllib3

http = urllib3.PoolManager()

class Nominatim:
    search_url:str = 'https://nominatim.openstreetmap.org/search?format=json'
    reverse_url:str = 'https://nominatim.openstreetmap.org/reverse?format=json'
    lookup_url:str = 'https://nominatim.openstreetmap.org/lookup?format=json'
    logger:Logger = getLogger(__name__)

    def query(self, url):
        self.logger.debug('querying the following url:\n' + url)
        result = http.request('GET', url).data
        return json.loads(result) if result != "" else None

    def search(self, query, accept_language='', limit=None):
        """Class for querying text address: https://nominatim.org/release-docs/develop/api/Search/
        Method takes query string, accept_language string (rfc2616 language code), limit integer (limits number of results)."""
        query = query.replace(' ', '+')
        url = self.search_url + '&q=' + query
        if accept_language:
            url += '&accept-language=' + accept_language
        if limit:
            url += '&limit=' + str(limit)
        return self.query(url)

    def reverse(self, lat=None, lon=None, accept_language='', zoom=18):
        """Method for querying gps coordinates: https://nominatim.org/release-docs/develop/api/Reverse/
        Method takes lat and lon for GPS coordinates, accept_language string, zoom integer (between from 0 to 18)."""
        url = self.reverse_url
        if lat and lon:
            url += '&lat=' + str(lat) + '&lon=' + str(lon)
        if accept_language:
            url += '&accept-language=' + accept_language
        if zoom < 0 or zoom > 18:
            raise Exception('zoom must be betwen 0 and 18')
        url +='&zoom=' + str(zoom)
        return self.query(url)

    def lookup(self, query:str):
        """Class for querying Ways, Nodes, etc. (Osm-IDs): https://nominatim.org/release-docs/develop/api/Lookup
        Method takes query string which must contain a comma-separated list of OSM ids each prefixed with its type, one of node(N), way(W) or relation(R)."""
        if query is None:
            return None
        if re.search('[NWR]\d{4,15}', query) is None:
            return None
        url = self.url
        url += '&osm_ids=' + query
        return self.query(url)