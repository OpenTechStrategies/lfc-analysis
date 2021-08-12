import mwclient
import config
from geopy.geocoders import Nominatim
import folium
from folium import FeatureGroup, LayerControl, Map, Marker
import pandas as pd
import sys

site = mwclient.Site('torque.leverforchange.org/', 'GlobalView/', scheme="https")
site.login(config.username, config.api_key)
geolocator = Nominatim(user_agent = "map")

def main():
    '''
    #Parse arguments
    competition = sys.argv[1]
    color = sys.argv[2]

    '''

    competition = "RacialEquity2030"
    color = 'blue'

    #Setup Map
    mapit = folium.Map()
    title_html = '''
                 <h3 align="center" style="font-size:16px"><b>Applicant Location Maps</b></h3>
                 '''.format()

    #Retrieve proposal ids from competition
    response = site.api(
        'torquedataconnect',
        format='json',
        path='/competitions/' + competition + '/proposals'
    )
    proposal_ids = response["result"]

    locations = extract_locations(proposal_ids, competition) #Extract locations from proposal ids
    df_locations = pd.DataFrame(locations, columns=['Lat', 'Long'])
    feature_group = FeatureGroup(competition)

    # Find SW and NE corners of the data
    sw = df_locations[['Lat', 'Long']].min().values.tolist()
    ne = df_locations[['Lat', 'Long']].max().values.tolist()

    for coord in locations:
        folium.CircleMarker(location=[coord[0], coord[1]],
                            fill_color=color, radius=5,
                            color = color, opacity = 0.5,
                            weight = 1).add_to(feature_group)
    feature_group.add_to(mapit)
    LayerControl().add_to(mapit)
    mapit.get_root().html.add_child(folium.Element(title_html))
    mapit.fit_bounds([sw, ne])
    mapit.save('applicant_locations_' + competition + '.html')

def extract_locations(proposal_ids, competition):

    error_list = []
    # Extract organization locations
    locations = []
    for id in proposal_ids:

        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + competition + '/proposals' + '/' + id
        )
        response['result']
        org_location = geolocator.geocode(
            concat_org_location(response['result'])) # Convert named address to latlong pair
        try:
            coordinate_pair = (org_location.latitude, org_location.longitude)
            locations.append(coordinate_pair)
        except:
            print('error, not a location')
            error_list.append([competition, id])
    df = pd.DataFrame(error_list)
    df.to_csv('error_file.csv')
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