import os

import requests
from environs import Env
from pprint import pprint
from fileinput import FileInput


def get_access_token(client_id):
    url_get_token = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'grant_type': 'implicit'
    }
    response = requests.post(url_get_token, data)
    response.raise_for_status()
    return response.json()['access_token']


def get_response_api(client_id, token, resource):
    access_token = token
    init_url = 'https://api.moltin.com'
    general_url = init_url + resource
    status_code = False
    while not status_code:
        headers = {'Authorization': f'Bearer {access_token}'}
        try:
            response = requests.get(general_url, headers=headers)
            response.raise_for_status()
            status_code = response.ok
        except requests.exceptions.HTTPError as err:
            access_token = get_access_token(client_id)
            os.environ['ACCESS_TOKEN'] = access_token
            for row in FileInput('.env', inplace=True):
                if row[:2] == 'ACC':
                    row = f'ACCESS_TOKEN={access_token}'
                else:
                    row = row[:-2]
                print(row)

    return response.json()


def main():
    env = Env()
    env.read_env()
    client_id = env('CLIENT_ID')
    access_token = env('ACCESS_TOKEN')
    products = get_response_api(client_id=client_id, token=access_token, resource='/catalog/products')
    pprint(products)


if __name__ == '__main__':
    main()

