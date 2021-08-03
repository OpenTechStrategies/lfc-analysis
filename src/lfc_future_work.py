import mwclient
import config
from geopy.geocoders import Nominatim
import folium
from folium import FeatureGroup, LayerControl, Map, Marker
import pandas as pd
import numpy as np
import sys
import json
site = mwclient.Site('torque.leverforchange.org/', 'GlobalView/', scheme="https")
site.login(config.username, config.api_key)
geolocator = Nominatim(user_agent = "map")

def main():

    competitions = ['LLIIA2020', 'LFC100Change2020', 'EO2020', 'RacialEquity2030', 'Climate2030', 'ECW2020', 'LoneStar2020']
    #competitions = ['LLIIA2020']
    #Setup Map
    mapit = folium.Map(location=[48, -102], zoom_start=6, )
    locations = [] # future work locations

    country_shapes = 'world_countries.json'
    with open(country_shapes) as f:
        map_data = json.loads(f.read())
    for i in range(len(competitions)):
        competition = competitions[i]

        #Retrieve proposal ids from competition
        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + competition + '/proposals'
        )
        proposal_ids = response["result"]

        # Extract locations and convert to dataframe of countries and counts
        locations.extend(extract_locations(proposal_ids, competition)) #Extract locations from proposal ids

    # Convert location list to dataframe with the country and number of occurrences
    np_locations = np.array(locations)
    values, counts = np.unique(np_locations, return_counts=True)
    country_data = pd.DataFrame(np.column_stack([values, counts]), columns=['country', 'occurrences'])
    country_data = country_data.astype({"country": str, "occurrences": 'int64'})

    # Scale data for map
    scale = list(country_data['occurrences'].quantile([0, 0.25, 0.5, 0.75, 1])) # Define scale

    # Graph data on choropleth map
    choropleth = folium.Choropleth(geo_data=map_data,
                      data=country_data,
                      columns=["country", "occurrences"],
                      key_on='feature.properties.name',
                      line_color='Blues', line_opacity=1,
                      fill_color='Blues',
                      nan_fill_color='white',
                      bins=scale).add_to(mapit)

    # Prepare labels for country tiles
    tooltip_text = []
    for index in range(len(country_data)):
        tooltip_text.append([country_data['country'][index], int(country_data['occurrences'][index])])
    np_tooltip_text = np.array(tooltip_text)

    #Append tooltip column to json file
    length = len(map_data['features'])
    for index in range(length):
        country_name = map_data['features'][index]['properties']['name']

        if country_name in np_tooltip_text[:,0]:
            map_data['features'][index]['properties']['tooltip1'] = np_tooltip_text[
                np.where(np_tooltip_text == country_name)[0][0], 1]
        else:
            map_data['features'][index]['properties']['tooltip1'] = 0

    # Add custom labels to country tiles
    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['tooltip1'], labels=False))

    # Title and save map

    mapit.save('future_work_map.html') # Save html


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
def extract_locations(proposal_ids, competition):
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