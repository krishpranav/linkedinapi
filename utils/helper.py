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
        return d_included["actor"]["name"]["text"]
    except KeyError:
        return ""
    except TypeError:
        return "None"


def get_update_old(d_included: Dict) -> str:
    try:
        return d_included["actor"]["subDescription"]["text"]
    except KeyError:
        return ""
    except TypeError:
        return "None"


def get_update_content(d_included: Dict, base_url: str) -> str:
    try:
        return d_included["commentary"]["text"]["text"]
    except KeyError:
        return ""
    except TypeError:
        try:
            urn = get_urn_from_raw_update(d_included["*resharedUpdate"])
            return f"{base_url}/feed/update/{urn}"
        except KeyError:
            return "IMAGE"
        except TypeError:
            return "None"


def get_update_author_profile(d_included: Dict, base_url: str) -> str:
    urn: str = ""
    try:
        urn = d_included["actor"]["urn"]
    except KeyError:
        return ""
    except TypeError:
        return "None"
    else:
        urn_id = urn.split(":")[-1]
        if "company" in urn:
            return f"{base_url}/company/{urn_id}"
        elif "member" in urn:
            return f"{base_url}/in/{urn_id}"
    return urn


def get_update_url(d_included: Dict, base_url: str) -> str:
    try:
        urn = d_included["updateMetadata"]["urn"]
    except KeyError:
        return ""
    except TypeError:
        return "None"
    else:
        return f"{base_url}/feed/update/{urn}"


def append_update_post_field_to_posts_list(
    d_included: Dict, l_posts: List, post_key: str, post_value: str
) -> List[Dict]:
    elements_current_index = len(l_posts) - 1

    if elements_current_index == -1:
        l_posts.append({post_key: post_value})
    else:
        if not post_key in l_posts[elements_current_index]:
            l_posts[elements_current_index][post_key] = post_value
        else:
            l_posts.append({post_key: post_value})
    return l_posts


def parse_list_raw_urns(l_raw_urns: List[str]) -> List[str]:
    l_urns = []
    for i in l_raw_urns:
        l_urns.append(get_urn_from_raw_update(i))
    return l_urns


def parse_list_raw_posts(l_raw_posts: List[Dict], linkedin_base_url: str) -> List[Dict]:
    l_posts = []
    for i in l_raw_posts:
        author_name = get_update_author_name(i)
        if author_name:
            l_posts = append_update_post_field_to_posts_list(
                i, l_posts, "author_name", author_name
            )

        author_profile = get_update_author_profile(i, linkedin_base_url)
        if author_profile:
            l_posts = append_update_post_field_to_posts_list(
                i, l_posts, "author_profile", author_profile
            )

        old = get_update_old(i)
        if old:
            l_posts = append_update_post_field_to_posts_list(i, l_posts, "old", old)

        content = get_update_content(i, linkedin_base_url)
        if content:
            l_posts = append_update_post_field_to_posts_list(
                i, l_posts, "content", content
            )

        url = get_update_url(i, linkedin_base_url)
        if url:
            l_posts = append_update_post_field_to_posts_list(i, l_posts, "url", url)

    return l_posts


def get_list_posts_sorted_without_promoted(
    l_urns: List[str], l_posts: List[Dict]
) -> List[Dict]:
    l_posts_sorted_without_promoted = []
    l_posts[:] = [d for d in l_posts if d and "Promoted" not in d.get("old", "")]
    for urn in l_urns:
        for post in l_posts:
            if urn in post["url"]:
                l_posts_sorted_without_promoted.append(post)
                l_posts[:] = [d for d in l_posts if urn not in d.get("url", "")]
                break
    return l_posts_sorted_without_promoted


def generate_trackingId_as_charString() -> str:
    random_int_array = [random.randrange(256) for _ in range(16)]
    rand_byte_array = bytearray(random_int_array)
    return "".join([chr(i) for i in rand_byte_array])


def generate_trackingId() -> str:
    random_int_array = [random.randrange(256) for _ in range(16)]
    rand_byte_array = bytearray(random_int_array)
    return str(base64.b64encode(rand_byte_array))[2:-1]