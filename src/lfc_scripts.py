import mwclient
import config

site = mwclient.Site('torque.leverforchange.org/', 'GlobalView/', scheme="https")
site.login(config.username, config.api_key)

response = site.api(
    'torquedataconnect',
    format='json',
    path='/competitions/LoneStar2020/proposals'
)

print(response["result"]) 