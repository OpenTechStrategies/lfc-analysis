import mwclient
import config
from geopy.geocoders import Nominatim
import folium

COMPETITION_NAME = "LFC100Change2020"
site = mwclient.Site('torque.leverforchange.org/', 'GlobalView/', scheme="https")
site.login(config.username, config.api_key)
geolocator = Nominatim(user_agent = "map")

def main():
    response = site.api(
        'torquedataconnect',
        format='json',
        path='/competitions/' + COMPETITION_NAME + '/proposals'
    )
    proposal_ids = response["result"]

    locations = extract_locations(proposal_ids)
    generate_map(locations)

def generate_map(locations):
    # Plot latlong points
    mapit = folium.Map(location=[48, -102], zoom_start=6)
    for coord in locations:
        folium.Marker(location=[coord[0], coord[1]], fill_color='#43d9de', radius=4).add_to(mapit)
    mapit.save('map1.html')

def extract_locations(proposal_ids):
    # Extract organization locations
    locations = []
    for id in proposal_ids:

        response = site.api(
            'torquedataconnect',
            format='json',
            path='/competitions/' + COMPETITION_NAME + '/proposals' + '/' + id
        )
        response['result']
        org_location = geolocator.geocode(
            concat_org_location(response['result']))  # Convert named address to latlong pair
        try:
            coordinate_pair = (org_location.latitude, org_location.longitude)
        except:
            print('error, not a location')
        locations.append(coordinate_pair)
    return locations

def concat_org_location(proposal):

    org_location = []
    for key, value in proposal.items():
        if key == "Org Locality/ District/ County":
            org_location.append(value)
        if key == "Org State/Province":
            org_location.append(value)
        if key == "Org Country":
            org_location.append(value)
    return org_location

if __name__ == "__main__":
    main()