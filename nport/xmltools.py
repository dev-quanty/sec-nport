from typing import Optional, Union
from decimal import Decimal
from bs4 import Tag, BeautifulSoup


__all__ = [
    'find_element',
    'child_text',
    'child_value',
    'optional_decimal_text',
    'optional_decimal_value'
]


def find_element(
        xml_tag_or_string: Union[str, BeautifulSoup, Tag], element_name) -> Tag:
    """
    Find the element with that name in the string or Tag
    :param xml_tag_or_string: either an exml tag or string containing xml
    :param element_name: The name of the element to find
    :return: An element
    """
    if isinstance(xml_tag_or_string, Tag):
        return xml_tag_or_string.find(element_name)
    elif isinstance(xml_tag_or_string, str) and "<" in xml_tag_or_string:
        soup: BeautifulSoup = BeautifulSoup(xml_tag_or_string, features="xml")
        return soup.find(element_name)


def child_text(parent: Tag, child: str) -> Optional[str]:
    """
    Get the text of the child element if it exists or None
    :param parent: The parent tag
    :param child: The name of the child element
    :return: the text of the child element if it exists or None
    """
    el = parent.find(child)
    if el and el.text.strip() != "N/A":
        return el.text.strip()
    return None


def child_value(parent: Tag, child: str, key: str = "value") -> Optional[str]:
    """
    Get the value of the child element if it exists or None
    :param parent: The parent tag
    :param child: The name of the child element
    :param key: The key of the child element's attributes
    :return: the value of the child element attribute if it exists or None
    """
    el = parent.find(child)
    if el:
        value = el.attrs.get(key)
        if value.strip() != "N/A":
            return value
    return None


def optional_decimal_text(parent: Tag, child: str) -> Optional[Decimal]:
    text = child_text(parent, child)
    if text:
        if text == "N/A" or text == "XXXX":
            return None
        return Decimal(text)
    return None


def optional_decimal_value(parent: Tag, child: str, key: str = "value") -> Optional[Decimal]:
    text = child_value(parent, child, key)
    if text:
        if text == "N/A" or text == "XXXX":
            return None
        return Decimal(text)
    return None
