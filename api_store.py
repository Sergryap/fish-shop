import os
import time
import requests


def get_products():
    url = 'https://api.moltin.com/catalog/products'
    headers = {'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_pcm_products():
    url = 'https://api.moltin.com/pcm/products'
    headers = {'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product_price(price_book_id, product_price_id):
    url = f'https://api.moltin.com/pcm/pricebooks/{price_book_id}/prices/{product_price_id}'
    headers = {'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product(product_id):
    url = f'https://api.moltin.com/pcm/products/{product_id}'
    headers = {'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}'}
    params = {'include': 'component_products'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def create_main_image_relationship(product_id, image_id):
    """Create a Product relationship to a single File, which can be used as a main_image"""
    url = f'https://api.moltin.com/v2/products/{product_id}/relationships/main_image'
    headers = {
        'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'data': {
            'type': 'main_image',
            'id': image_id
        }
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()


def create_file_relationships(product_id, image_ids: list):
    """Create a product relationship to one or more Files"""
    url = f'https://api.moltin.com/v2/products/{product_id}/relationships/files'
    headers = {
        'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'data': [{'type': 'file', 'id': image_id} for image_id in image_ids]
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()


def upload_image(path_to_file):
    with open(path_to_file, 'rb') as file:
        url = 'https://api.moltin.com/v2/files'
        headers = {
            'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
            'Content-Type': 'multipart/form-data',
        }
        files = {'file': file}
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()


def get_file(file_id):
    url = f'https://api.moltin.com/v2/files/{file_id}'
    headers = {'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart(reference):
    url = f'https://api.moltin.com/v2/carts/{reference}'
    headers = {
        'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart_items(reference):
    url = f'https://api.moltin.com/v2/carts/{reference}/items'
    headers = {
        'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def create_cart(name, description='fish-order'):
    url = 'https://api.moltin.com/v2/carts'
    headers = {
        'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
        'Content-Type': 'application/json',
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


def add_product_to_cart(product_id, quantity, reference):
    url = f'https://api.moltin.com/v2/carts/{reference}/items'
    headers = {
        'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
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


def remove_cart_item(reference, product_id):
    url = f'https://api.moltin.com/v2/carts/{reference}/items/{product_id}'
    headers = {'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}'}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()


def create_customer(name, email, password=None):
    url = 'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
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


def get_customer(customer_id):
    url = f'https://api.moltin.com/v2/customers/{customer_id}'
    headers = {
        'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def generate_customer_token(email, password):
    url = 'https://api.moltin.com/v2/customers/tokens'
    headers = {
        'Authorization': f'Bearer {os.environ["ACCESS_TOKEN"]}',
        'Content-Type': 'application/json'
    }
    json_data = {
        'data': {
            'type': 'token',
            'email': email,
            'password': password,
        }
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()


def check_token(err=False):
    if not os.environ.get('TOKEN_EXPIRES') or int(os.environ['TOKEN_EXPIRES']) < int(time.time()) or err:
        url = 'https://api.moltin.com/oauth/access_token'
        client_id = os.getenv('CLIENT_ID')
        client_secret = os.getenv('CLIENT_SECRET')
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, data)
        response.raise_for_status()
        token_data = response.json()
        os.environ['TOKEN_EXPIRES'] = str(token_data['expires'] - 60)
        os.environ['ACCESS_TOKEN'] = token_data['access_token']
