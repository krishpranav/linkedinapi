'''
@author: Krisna Pranav
@filename: helper.py
@date: 17 April 2025
'''

import random
import base64
from typing import Dict, List

def get_id_from_urn(urn: str):
    return urn.split(":")[3]

def get_urn_from_raw_update(raw_string: str) -> str:
    return raw_string.split("(")[1].split(",")[0]

def get_update_author_name(d_included: Dict) -> str:
    try:
        return d_included["action"]["name"]["text"]
    except KeyError:
        return ""
    except TypeError:
        return "None"

def generate_trackingId_as_charString() -> str:
    random_int_array = [random.randrange(256) for _ in range(16)]
    rand_byte_array = bytearray(random_int_array)
    return "".join([chr(i) for i in rand_byte_array])

def generate_trackingId() -> str:
    random_int_array = [random.randrange(256) for _ in range(16)]
    rand_byte_array = bytearray(random_int_array)
    return str(base64.b64encode(rand_byte_array))[2:-1]