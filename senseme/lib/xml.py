"""Helpers for dealing with XML."""

import xml.etree.ElementTree as ET


def data_to_xml(d, name='data'):
    """Convert data to XML."""
    r = ET.Element(name)
    return ET.tostring(build_xml(r, d))


def build_xml(r, d):
    """Build XML recursively."""
    if isinstance(d, dict):
        for k, v in d.items():
            s = ET.SubElement(r, k)
            build_xml(s, v)
    elif isinstance(d, tuple) or isinstance(d, list):
        for v in d:
            s = ET.SubElement(r, 'i')
            build_xml(s, v)
    elif isinstance(d, str):
        r.text = d
    else:
        r.text = str(d)
    return r
