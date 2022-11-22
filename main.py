import requests
from environs import Env
from pprint import pprint


def get_access_token(client_id):
    url_get_token = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'grant_type': 'implicit'
    }
    response = requests.post(url_get_token, data)
    response.raise_for_status()
    return response.json()['access_token']


def get_response_api(token, resource):
    access_token = token
    init_url = 'https://api.moltin.com'
    general_url = init_url + resource
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(general_url, headers=headers)
    response.raise_for_status()

    return response.json()


def main():
    env = Env()
    env.read_env()
    client_id = env('CLIENT_ID')
    access_token = env('ACCESS_TOKEN')
    # access_token = get_access_token(client_id)
    products = get_response_api(token=access_token, resource='/catalog/products')
    pprint(products)


if __name__ == '__main__':
    main()
