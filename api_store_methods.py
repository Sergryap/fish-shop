import os

import requests
from environs import Env
from pprint import pprint
from fileinput import FileInput


def get_access_token(client_id, client_secret):
    url = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data)
    response.raise_for_status()

    return response.json()['access_token']


def get_products(token):
    url = 'https://api.moltin.com/catalog/products'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_product_price(token, price_book_id, product_price_id):
    url = f'https://api.moltin.com/pcm/pricebooks/{price_book_id}/prices/{product_price_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    # response.raise_for_status()

    return response.json()


def get_product(token, product_id):
    url = f'https://api.moltin.com/pcm/products/{product_id}'
    headers = {'Authorization': f'Bearer {token}'}
    params = {'include': 'component_products'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def get_cart(token, reference):
    url = f'https://api.moltin.com/v2/carts/{reference}'
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def create_cart(token, name, description='fish-order'):
    url = 'https://api.moltin.com/v2/carts'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        # 'x-moltin-customer-token': customer_token
    }
    json_data = {
        'data': {
            'name': name,
            'description': description
        }
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()

    return response.json()


def add_product_to_cart(token, product_id, quantity, reference):
    url = f'https://api.moltin.com/v2/carts/{reference}/items'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': quantity,
        }
    }
    response = requests.post(url=url, headers=headers, json=json_data)
    response.raise_for_status()

    return response.json()


def generate_customer_token(token, email, password):
    access_token = token
    url = 'https://api.moltin.com/v2/customers/tokens'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    json_data = {
        'data': {
            'type': 'token',
            'email': email,
            'password': password,
            # "authentication_mechanism": "password"
        }
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()

    return response.json()


def method_api(func, *args, **kwargs):
    status_token = False
    count = 0
    while not status_token:
        try:
            status_token = True
            result = func(os.getenv('ACCESS_TOKEN'), *args, **kwargs)
        except requests.exceptions.HTTPError as err:
            count += 1
            if count == 4:
                msg = f'Ошибка: {err}'
                print(msg)
                return msg
            status_token = False
            access_token = get_access_token(os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
            os.environ['ACCESS_TOKEN'] = access_token
            for n, row in enumerate(FileInput('.env', inplace=True)):
                if n == 0:
                    row = f'ACCESS_TOKEN={access_token}'
                else:
                    row = row[:-1]
                print(row)
    return result


def main():
    env = Env()
    env.read_env()
    client_id = env('CLIENT_ID')
    client_secret = env('CLIENT_SECRET')
    access_token = env('ACCESS_TOKEN')
    customer_token = env('CUSTOMER_TOKEN')
    customer_id = env('CUSTOMER_ID')
    customer_email = env('CUSTOMER_EMAIL')
    customer_password = env('CUSTOMER_PASSWORD')
    products = method_api(get_products)
    # product = method_api(get_product, product_id='4f405bed-cb79-42cc-aeed-4fd8fe83c81c')
    # price = method_api(get_product_price, price_book_id='419f9492-4b11-4605-b16d-a8ab8938b080', product_price_id='4f405bed-cb79-42cc-aeed-4fd8fe83c81c')
    # customer_token = method_api(generate_customer_token, email=customer_email, password=customer_password)
    # cart = method_api(create_cart, name='Cart', description='test-1')
    # cart = method_api(get_cart, reference='Cart')
    # product_to_cart = method_api(
    #     add_product_to_cart,
    #     product_id='4f405bed-cb79-42cc-aeed-4fd8fe83c81c',
    #     quantity=1,
    #     reference='Cart'
    # )
    pprint(products)


if __name__ == '__main__':
    main()
