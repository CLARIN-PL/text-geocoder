from xml.etree import ElementTree


def extract_locations(file_path):

    attributes = {'city_nam', 'country_nam', 'road_nam'}

    xml_iter = ElementTree.iterparse(file_path, events=('start', 'end'))

    locations = list()
    current_base = ''

    for event, elem in xml_iter:
        if event == 'start':
            if elem.tag == 'base' and elem.tag != '':
                    current_base = elem.text
            if elem.tag == 'ann' and elem.attrib['chan'] in attributes and elem.text != '0':
                item = {'base': current_base,
                        'attr': elem.attrib['chan'], 'occurrences': 1}
                item_occurred = False
                for l in locations:
                    if l['base'] == item['base'] and l['attr'] == item['attr']:
                        l['occurrences'] += 1
                        item_occurred = True

                if not item_occurred:
                    locations.append(item)
    return locations

