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
    competitions = ['LLIIA2020', 'LFC100Change2020', 'EO2020', 'RacialEquity2030', 'Climate2030', 'ECW2020', 'LoneStar2020'] # LFC100Change2017 left out
    #competitions = ['Climate2030', 'ECW2020']
    #duplicates = ['Arizona State University', 'CARE', 'Forterra NW', 'GRID Alternatives', 'Local Initiatives Support Corporation', 'Mercy Corps', 'Rocky Mountain Institute']

    colors = ['blue', 'red', 'pink', 'purple', 'black', 'green', 'grey']

    # Setup Map
    mapit = folium.Map(location=[48, -102], zoom_start=6)

    for i in range(len(competitions)):
        competition = competitions[i]
        color = colors[i]
        loc = 'Corpus Christi'
        title_html = '''
                     <h3 align="center" style="font-size:16px"><b>Top 25 Proposals</b></h3>
                     '''.format(loc)

        #Retrieve proposal ids from competition
        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + competition + '/proposals'
        )
        proposal_ids = response["result"]

        org_names, locations = extract_top_25_info(proposal_ids, competition) #Extract locations from proposal ids
        duplicates = return_duplicate_orgs(org_names) # Returns organizations that have more than one proposal in top 25

        feature_group = FeatureGroup(competition)
        for i in range(len(locations)):
            coord = locations[i]
            try:
                if org_names[i] in duplicates:
                    folium.CircleMarker(location=[coord[0], coord[1]], fill_color=color, radius=14, color = color, opacity = 0.5, weight = 1).add_to(feature_group)
                else:
                    folium.CircleMarker(location=[coord[0], coord[1]], fill_color=color, radius=7, color=color, opacity=0.5, weight=1).add_to(feature_group)
            except:
                print("Failed mapping")
        feature_group.add_to(mapit)
    LayerControl().add_to(mapit)
    mapit.get_root().html.add_child(folium.Element(title_html))
    mapit.save('top_25_map.html')


def extract_top_25_info(proposal_ids, competition):
    # Org name lookup
    org_name_lookup = {
        'LLIIA2020': ['Organization Name'],
        'LFC100Change2020': ['Organization Legal Name'],
        'EO2020': ['Organization Name'],
        'RacialEquity2030': ['Organization name'],
        'Climate2030': ['Organization Name'],
        'ECW2020': ['Organization Name'],
        'LoneStar2020': ['Organization Name']}
    # Org names
    org_names = []

    # Extract organization locations
    locations = []
    for i in np.arange(0,25):
        id = proposal_ids[i]
        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + competition + '/proposals' + '/' + id
        )

        location = concat_org_location(response['result'])
        for key, value in response['result'].items():
            if key in org_name_lookup[competition]:
                org_names.append(value)

        location_object = geolocator.geocode(location)  # Convert named address to latlong pair
        try:
            coordinate_pair = (location_object.latitude, location_object.longitude)
            locations.append(coordinate_pair)
        except:
            print('error, not a location')
            locations.append(())


    return org_names, locations

def return_duplicate_orgs(org_names):
    np_org_names = np.array(org_names)
    unique_names, counts = np.unique(np_org_names, return_counts=True)
    duplicates = unique_names[counts > 1]
    return duplicates

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