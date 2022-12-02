import os
import requests
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


def get_pcm_products(token):
    url = 'https://api.moltin.com/pcm/products'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product_price(token, price_book_id, product_price_id):
    url = f'https://api.moltin.com/pcm/pricebooks/{price_book_id}/prices/{product_price_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product(token, product_id):
    url = f'https://api.moltin.com/pcm/products/{product_id}'
    headers = {'Authorization': f'Bearer {token}'}
    params = {'include': 'component_products'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def create_main_image_relationship(token, product_id, image_id):
    """Create a Product relationship to a single File, which can be used as a main_image"""
    url = f'https://api.moltin.com/v2/products/{product_id}/relationships/main-image'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'data': {
            'type': 'main_image',
            'id': image_id
        }
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()


def create_file_relationships(token, product_id, image_ids: list):
    """Create a product relationship to one or more Files"""
    url = f'https://api.moltin.com/v2/products/{product_id}/relationships/files'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'data': [{'type': 'file', 'id': image_id} for image_id in image_ids]
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()


def upload_image(token, path_to_file):

    with open(path_to_file, 'rb') as file:
        url = 'https://api.moltin.com/v2/files'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'multipart/form-data',
        }
        files = {'file': file}
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()


def get_file(token, file_id):
    url = f'https://api.moltin.com/v2/files/{file_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
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


def get_cart_items(token, reference):
    url = f'https://api.moltin.com/v2/carts/{reference}/items'
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


def remove_cart_item(token, reference, product_id):
    url = f'https://api.moltin.com/v2/carts/{reference}/items/{product_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()


def create_customer(token, name, email, password=None):
    url = 'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    data = {
        'type': 'customer',
        'name': name,
        'email': email,
        'password': password,
    }
    json_data = {
        'data': {key: value for key, value in data.items() if value is not None}
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()


def get_customer(token, customer_id):
    url = f'https://api.moltin.com/v2/customers/{customer_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
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
    token_status = False
    while not token_status:
        try:
            token_status = True
            result = func(os.getenv('ACCESS_TOKEN'), *args, **kwargs)
        except requests.exceptions.HTTPError:
            token_status = False
            os.environ['ACCESS_TOKEN'] = get_access_token(os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
    return result
