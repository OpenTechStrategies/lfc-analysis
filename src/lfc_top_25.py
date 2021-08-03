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
    mapit = folium.Map(location=[48, -102], zoom_start=6)

    # Import extra data
    df_extra_data = pd.read_csv('highly_ranked_proposals.csv')

    # Create institution type feature groups
    fg_NGO = FeatureGroup("NGO")
    fg_academic = FeatureGroup("Academic Institution")
    for index, row in df_extra_data.iterrows():
        competition = row['Competition']
        id = str(row['ID'])

        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + competition + '/proposals' + '/' + id
        )

        proposal = response['result']

        coord = extract_top_25_locations(proposal, competition) # Extract Location

        if coord == ():
            print("Empty coordinate")
        else:
            # Map Location

            # Create square icon
            icon_square = folium.plugins.BeautifyIcon(
                icon_shape='rectangle-dot',
                border_color='red', opacity=0.5,
                border_width=7
            )

            if row['Type'] == 'NGO':
                folium.CircleMarker(location=[coord[0], coord[1]],
                                    fill_color='blue', radius=3.5,
                                    color='blue', opacity=0.5,
                                    weight=1).add_to(fg_NGO)
            else:

                folium.Rectangle(bounds=create_square_bounds(coord, 0.1),
                                 color='red', fill=True,
                                 fill_color='red',
                                 fill_opacity=0.2, opacity=0.5).add_to(fg_academic)
    fg_NGO.add_to(mapit)
    fg_academic.add_to(mapit)
    LayerControl().add_to(mapit)
    #mapit.get_root().html.add_child(folium.Element(title_html))
    mapit.save('top_25_map.html')

def create_square_bounds(coord, side_length):

    W = coord[1] - side_length
    E = coord[1] + side_length
    N = coord[0] + side_length
    S = coord[0] - side_length

    upper_left = (N, W)
    upper_right = (N, E)
    lower_right = (S, E)
    lower_left = (S, W)

    return [upper_left, upper_right, lower_right, lower_left]
def extract_top_25_locations(proposal, competition):
    # Org name lookup
    org_name_lookup = {
        'LLIIA2020': ['Organization Name'],
        'LFC100Change2020': ['Organization Legal Name'],
        'EO2020': ['Organization Name'],
        'RacialEquity2030': ['Organization name'],
        'Climate2030': ['Organization Name'],
        'ECW2020': ['Organization Name'],
        'LoneStar2020': ['Organization Name']}

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