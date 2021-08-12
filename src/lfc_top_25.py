import mwclient
import config
from geopy.geocoders import Nominatim
import folium
from folium import FeatureGroup, LayerControl, Map, Marker
import pandas as pd
import numpy as np
import sys
from folium import plugins
site = mwclient.Site('torque.leverforchange.org/', 'GlobalView/', scheme="https")
site.login(config.username, config.api_key)
geolocator = Nominatim(user_agent = "map")

def main():

    # Setup Map
    mapit = folium.Map()

    # Import extra data
    df_extra_data = pd.read_csv('highly_ranked_proposals.csv')

    # Create institution type feature groups
    fg_NGO = FeatureGroup("NGO")
    fg_academic = FeatureGroup("Academic Institution")

    locations = [] # Locations list
    for index, row in df_extra_data.iterrows():
        competition = row['Competition']
        id = str(row['ID'])

        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + competition + '/proposals' + '/' + id
        )

        proposal = response['result']

        coord = extract_top_25_locations(proposal) # Extract Location
        locations.append(coord)

        # Map Location
        if row['Type'] == 'NGO':
            folium.CircleMarker(location=[coord[0], coord[1]],
                                fill_color='blue', radius=5,
                                color='blue', opacity=0.5,
                                weight=1).add_to(fg_NGO)
        else:

            folium.CircleMarker(location=[coord[0], coord[1]],
                                fill_color='red', radius=5,
                                color='red', opacity=0.5,
                                weight=1).add_to(fg_academic)
    fg_NGO.add_to(mapit)
    fg_academic.add_to(mapit)
    LayerControl().add_to(mapit)

    # Find NE and SW corners
    df_locations = pd.DataFrame(locations, columns=['Lat', 'Long'])
    sw = df_locations[['Lat', 'Long']].min().values.tolist()
    ne = df_locations[['Lat', 'Long']].max().values.tolist()

    mapit.fit_bounds([sw, ne])
    mapit.save('top_25_map.html')


def extract_top_25_locations(proposal):

    location = concat_org_location(proposal)
    location_object = geolocator.geocode(location)  # Convert named address to latlong pair
    try:
        coordinate_pair = (location_object.latitude, location_object.longitude)
    except:
        print('error, not a location')
        coordinate_pair = ()

    return coordinate_pair

def return_duplicate_orgs(org_names):
    np_org_names = np.array(org_names)
    unique_names, counts = np.unique(np_org_names, return_counts=True)
    duplicates = unique_names[counts > 1]
    return duplicates

def concat_org_location(proposal):

    org_location = []
    try:

        for key, value in proposal.items():

            if key == "City":
                org_location.append(value)
            if key == "Org Country" or key == "Country" or key == "Nation":
                org_location.append(value)
    except:
        print("Spreadsheet mistake")
    return org_location

if __name__ == "__main__":
    main()