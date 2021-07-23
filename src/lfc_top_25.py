import mwclient
import config
from geopy.geocoders import Nominatim
import folium
from folium import FeatureGroup, LayerControl, Map, Marker
import pandas as pd
import numpy as np
import sys

site = mwclient.Site('torque.leverforchange.org/', 'GlobalView/', scheme="https")
site.login(config.username, config.api_key)
geolocator = Nominatim(user_agent = "map")

def main():
    #Parse arguments
    '''
    competition = sys.argv[1]
    map_type = sys.argv[2]
    color = sys.argv[3]
    '''

    #Replace arguments
    competition = 'LoneStar2020'
    map_type = 'top_25'
    color = 'blue'
    #Setup Map
    mapit = folium.Map(location=[48, -102], zoom_start=6)
    loc = 'Corpus Christi'
    title_html = '''
                 <h3 align="center" style="font-size:16px"><b>Applicant Location Maps</b></h3>
                 '''.format(loc)

    #Retrieve proposal ids from competition
    response = site.api(
        'torquedataconnect',
        format='json',
        path='/competitions/' + competition + '/proposals'
    )
    proposal_ids = response["result"]

    locations = extract_locations_top_25(proposal_ids, competition, map_type) #Extract locations from proposal ids

    feature_group = FeatureGroup(competition)
    for coord in locations:
        folium.CircleMarker(location=[coord[0], coord[1]], fill_color=color, radius=7, color = color, opacity = 0.5, weight = 1).add_to(feature_group)
    feature_group.add_to(mapit)
    LayerControl().add_to(mapit)
    mapit.get_root().html.add_child(folium.Element(title_html))
    mapit.save(map_type + '_' + competition + '.html')


def extract_locations_top_25(proposal_ids, competition, map_type):

    # Extract organization locations
    locations = []
    for i in np.arange(0,25):
        id = proposal_ids[i]
        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + competition + '/proposals' + '/' + id
        )

        location_string = concat_org_location(response['result'])

        for location in location_string:
            location_object = geolocator.geocode(location)  # Convert named address to latlong pair
            try:
                coordinate_pair = (location_object.latitude, location_object.longitude)
                locations.append(coordinate_pair)
            except:
                print('error, not a location')
    return locations

def concat_org_location(proposal):

    org_location = []
    for key, value in proposal.items():

        if key == "City":
            org_location.append(value)
        if key == "Org Country" or key == "Country" or key == "Nation":
            org_location.append(value)

    return org_location

if __name__ == "__main__":
    main()