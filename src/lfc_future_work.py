import mwclient
import config
from geopy.geocoders import Nominatim
import folium
from folium import FeatureGroup, LayerControl, Map, Marker
import pandas as pd
import numpy as np
import sys
import branca.colormap as cm
from branca.colormap import linear
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
    competition = 'LFC100Change2020'
    map_type = 'future_work'
    color = 'blue'
    #Setup Map
    mapit = folium.Map(location=[48, -102], zoom_start=6, )
    loc = 'Corpus Christi'
    title_html = '''
                 <h3 align="center" style="font-size:16px"><b>Future Work Location Maps</b></h3>
                 '''.format(loc)
    country_shapes = 'world_countries.json'
    #Retrieve proposal ids from competition
    response = site.api(
        'torquedataconnect',
        format='json',
        path='/competitions/' + competition + '/proposals'
    )
    proposal_ids = response["result"]

    # Extract locations and convert to dataframe of countries and counts
    locations = extract_locations(proposal_ids, competition, map_type) #Extract locations from proposal ids
    np_locations = np.array(locations)
    values, counts = np.unique(np_locations, return_counts=True)
    country_data = pd.DataFrame(np.column_stack([values, counts]), columns=['country', 'occurrences'])

    #Convert Data type
    country_data = country_data.astype({"country": str, "occurrences": int})
    # country_data = replace_outliers(country_data)
    print(country_data.dtypes)

    # Put occurrence data on log scale
    #country_data['occurrences'] = np.log(country_data['occurrences'])
    min = country_data['occurrences'].min()
    max = country_data['occurrences'].max()
    #scale = np.geomspace(min, max, num = 10, endpoint = True)

    scale = list(country_data['occurrences'].quantile([0, 0.25, 0.5, 0.75, 1]))

    folium.Choropleth(geo_data=country_shapes,
                      data=country_data,
                      columns=["country", "occurrences"],
                      key_on='feature.properties.name',
                      line_color='Blues', line_opacity=1,
                      fill_color='Blues',
                      nan_fill_color='white',
                      bins=scale).add_to(mapit)

    mapit.get_root().html.add_child(folium.Element(title_html)) # Add title
    mapit.save(map_type + '_' + competition + '.html') # Save html
def replace_outliers(country_data):

    # If row is not equal to United States or India
    placeholder_data = country_data[(country_data['country'] != "United States") & (country_data['country'] != "India")]
    # Find max value
    max_value = max(placeholder_data['occurrences'])
    # Replace United States and India with maximum value
    try:
        test = country_data[(country_data['country'] == "United States") | (country_data['country'] == "India")]['occurrences']
        country_data['occurrences'] = country_data['occurrences'].replace([test], max_value)

    except:
        print("Data does not have country")
    return country_data
def extract_locations(proposal_ids, competition, map_type):
    # Extract locations
    locations = []
    for id in proposal_ids:

        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + competition + '/proposals' + '/' + id
        )

        location_string = concat_future_work_locations(response['result'], competition)

        locations.extend(location_string)
    locations = list(filter(None, locations))
    return locations

def concat_org_location(proposal):

    org_location = []
    for key, value in proposal.items():

        if key == "City":
            org_location.append(value)
        if key == "Org Country" or key == "Country" or key == "Nation":
            org_location.append(value)

    return org_location


def concat_future_work_locations(proposal, competition):

    future_work_lookup = {
        'LLIIA2020': ['Location of Future Work #1 Country', 'Location of Future Work #2 Country', 'Location of Future Work #3 Country', 'Location of Future Work #4 Country', 'Location of Future Work #5 Country'],
        'LFC100Change2020': ['Location Of Future Work Country', 'Location Of Future Work2 Country', 'Location Of Future Work3 Country', 'Location Of Future Work4 Country', 'Location Of Future Work5 Country'],
        'EO2020': ['Location of Future Work #1 Nation', 'Location of Future Work #2 Nation', 'Location of Future Work #3 Nation', 'Location of Future Work #4 Nation', 'Location of Future Work #5 Nation'],
        'RacialEquity2030': ['Location of Future Work #1 Country', 'Location of Future Work #2 Country', 'Location of Future Work #3 Country', 'Location of Future Work #4 Country', 'Location of Future Work #5 Country'],
        'Climate2030': ['Location of Future Work #1 Country', 'Location of Future Work #2 Country', 'Location of Future Work #3 Country', 'Location of Future Work #4 Country', 'Location of Future Work #5 Country'],
        'ECW2020': ['Location of Future Work #1 Country', 'Location of Future Work #2 Country', 'Location of Future Work #3 Country', 'Location of Future Work #4 Country', 'Location of Future Work #5 Country'],
        'LoneStar2020': ['Location of Future Work #1 Country', 'Location of Future Work #2 Country', 'Location of Future Work #3 Country', 'Location of Future Work #4 Country', 'Location of Future Work #5 Country']}

    future_work_locations = []

    for key, value in proposal.items():
        if key in future_work_lookup[competition]:
            future_work_locations.append(value)

    np_future_work = np.array(future_work_locations)
    return np_future_work

if __name__ == "__main__":
    main()