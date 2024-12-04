import json
from asyncio import timeout
from logging import Logger, getLogger

import urllib3
from urllib3.exceptions import NameResolutionError

from bewegungskalender.libs.exceptions import NoResultError

http = urllib3.PoolManager()

SEARCH_URL:str = 'https://nominatim.openstreetmap.org/search?format=json'
REVERSE_URL:str = 'https://nominatim.openstreetmap.org/reverse?format=json'
LOOKUP_URL:str = 'https://nominatim.openstreetmap.org/lookup?format=json'
LOGGER:Logger = getLogger(__name__)

def _query(url):
    LOGGER.debug('querying the following url:\n' + url)
    headers = {
        'User-Agent': 'Bewegungskalender',
        'From': 'bewegungskalender@systemli.org'  # This is another valid field
    }
    try:
        result = http.request('GET', url, headers=headers).data
    except NameResolutionError:
        LOGGER.warning("Exceeding API Limit - A Timeout is necessary.")
        timeout(60.0)
    else:
        if not result or result == b'[]':
            raise NoResultError(url)
        return json.loads(result)

def search(query, accept_language='', limit=None):
    """Class for querying text address: https://nominatim.org/release-docs/develop/api/Search/
    Method takes query string, accept_language string (rfc2616 language code), limit integer (limits number of results)."""
    query = query.replace(' ', '+')
    url = SEARCH_URL + '&q=' + query
    if accept_language:
        url += '&accept-language=' + accept_language
    if limit:
        url += '&limit=' + str(limit)
    return _query(url)

def search_city(query, accept_language='', limit=None):
    """Class for querying text address: https://nominatim.org/release-docs/develop/api/Search/
    Method takes query string, accept_language string (rfc2616 language code), limit integer (limits number of results)."""
    query = query.replace(' ', '+')
    url = SEARCH_URL + '&q=' + query
    if accept_language:
        url += '&accept-language=' + accept_language
    if limit:
        url += '&limit=' + str(limit)
    url += '&featureType=city'
    return _query(url)

def reverse(lat=None, lon=None, accept_language='', zoom=18):
    """Method for querying gps coordinates: https://nominatim.org/release-docs/develop/api/Reverse/
    Method takes lat and lon for GPS coordinates, accept_language string, zoom integer (between from 0 to 18)."""
    url = REVERSE_URL
    if lat and lon:
        url += '&lat=' + str(lat) + '&lon=' + str(lon)
    if accept_language:
        url += '&accept-language=' + accept_language
    if zoom < 0 or zoom > 18:
        raise ValueError('Zoom must be between 0 and 18')
    url +='&zoom=' + str(zoom)
    return _query(url)

def lookup_entity(link:str):
    """Class for querying Ways, Nodes, etc. (Osm-IDs): https://nominatim.org/release-docs/develop/api/Lookup
    Method takes a Match object matching a link directly to an OSM entity - either a node(N), a way(W) or a relation(R)."""
    # Extract the entity type and ID
    entity_type = link.split('/')[-2]
    entity_id = link.split('/')[-1]
    # Merge them together for the query url
    url = LOOKUP_URL + '&osm_ids=' + entity_type.upper()[0] + entity_id
    return _query(url)
