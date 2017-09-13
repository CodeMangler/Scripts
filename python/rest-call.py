from restkit import OAuthFilter
from restkit import Resource
import oauth2
import sys
import ConfigParser
 
def rest_call(url, method, data, headers, client_auth_key, client_auth_secret):
    consumer = oauth2.Consumer(key=client_auth_key, secret=client_auth_secret)
    auth = OAuthFilter('*',consumer)
    resource = Resource(url, filters=[auth])
    response = resource.request(method, payload=data, headers=headers, params=None)
    json_string = response.body_string()
    status = response.status
    return status, json_string

def main(url, method, data, headers, config_file='keys.conf'):
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    auth_key = config.get('auth', 'key')
    auth_secret = config.get('auth', 'secret')
    print rest_call(url, method, data, headers, auth_key, auth_secret)

if __name__ == '__main__':
    headers = {'Content-Type': 'text/plain'}
    config = 'keys.conf'
    if(len(sys.argv) > 4):
        headers = sys.argv[4]
    if(len(sys.argv) > 5):
        config = sys.argv[5]
    main(sys.argv[1], sys.argv[2], sys.argv[3], headers, config)
