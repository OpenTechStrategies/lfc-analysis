import mwclient
import config
from geopy.geocoders import Nominatim
import folium
from folium import FeatureGroup, LayerControl, Map, Marker


competitions = ["LLIIA2020", "LFC100Change2020", "LFC100Change2017", "EO2020", "RacialEquity2030", "Climate2030", "ECW2020", "LoneStar2020"]

site = mwclient.Site('torque.leverforchange.org/', 'GlobalView/', scheme="https")
site.login(config.username, config.api_key)
geolocator = Nominatim(user_agent = "map")

def main():
    mapit = folium.Map(location=[48, -102], zoom_start=6)
    for competition in competitions:
        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + competition + '/proposals'
        )
        proposal_ids = response["result"]

        locations = extract_locations(proposal_ids, competition)

        feature_group = FeatureGroup(competition)
        for coord in locations:
            folium.Marker(location=[coord[0], coord[1]], fill_color='#43d9de', radius=4).add_to(feature_group)
        feature_group.add_to(mapit)
    LayerControl().add_to(mapit)
    mapit.save('map1.html')


def extract_locations(proposal_ids, competition):
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
            concat_org_location(response['result']))  # Convert named address to latlong pair
        try:
            coordinate_pair = (org_location.latitude, org_location.longitude)
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
        """
        if key == "Street Address":
            org_location.append(value)
        if "Locality" in key or "District" in key or "County" in key:
            org_location.append(value)
        if "State" in key or "Province" in key:
            org_location.append(value)
        """
    return org_location

if __name__ == "__main__":
    main()