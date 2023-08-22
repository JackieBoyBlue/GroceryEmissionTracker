import requests
import os
from json import loads


class Asprise:
    """A class for interacting with the Asprise API."""

    @staticmethod
    def get_receipt_data(img: bytes, ref: str) -> str:
        """Gets the receipt data from the Asprise API."""

        if not isinstance(img, bytes): raise TypeError('img must be bytes')
        if not isinstance(ref, str): raise TypeError('ref must be a string')

        asprise_api_uri = 'https://ocr.asprise.com/api/v1/receipt'

        r = requests.post(asprise_api_uri, data = { \
            'api_key': os.getenv('ASPRISE_API_KEY', 'TEST'),
            'recognizer': 'GB',
            'ref_no': ref,
        },  \
        files = {"file": img})

        return r.text
    
    @staticmethod
    def extract_items_from_response(response: str) -> dict:
        """Extracts the items from the response from the Asprise API."""

        if not isinstance(response, str): raise TypeError('response must be a string')

        output = {}
        r_items = loads(response)['receipts'][0]['items']

        for item in r_items:
            output[item['description']] = item['amount']

        return output
