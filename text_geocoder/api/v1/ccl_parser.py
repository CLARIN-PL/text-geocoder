import itertools
from operator import itemgetter
from xml.etree import ElementTree

attributes = {
        'top9': {
            'location': 'nam_loc',
            'facility': 'nam_fac',
            'number': 'nam_num',
        },
        'n82': {
            'city': 'nam_loc_gpe_city',
            'country': 'nam_loc_gpe_country',
            'street': 'nam_fac_road',
            'square': ' nam_fac_square',
            'park': 'nam_fac_park',
            'bridge': 'nam_fac_bridge',
            'district': 'nam_loc_gpe_district',
            'bay': 'nam_loc_hydronym_bay',
            'lagoon': 'nam_loc_hydronym_lagoon',
            'lake': 'nam_loc_hydronym_lake',
            'ocean': 'nam_loc_hydronym_ocean',
            'river': 'nam_loc_hydronym_river',
            'sea': 'nam_loc_hydronym_sea',
            'house_number': 'nam_num_house',
            'flat_number': 'nam_num_flat',
            'postal_code': 'nam_num_postal_code',
            'cape': 'nam_loc_land_cape',
            'continent': 'nam_loc_land_continent',
            'desert': 'nam_loc_land_desert',
            'island': 'loc_land_island',
            'mountain': 'nam_loc_land_mountain',
            'peak': 'nam_loc_land_peak',
            'peninsula': 'nam_loc_land_peninsula',
            'protected_area': 'nam_loc_land_protected_area'
        }
}


def extract_locations(file_path, model):

    xml_iter = ElementTree.iterparse(file_path, events=('start', 'end'))

    annotations = list()

    current_orth = ''
    current_base = ''
    current_sentence = ''
    ann_id = 1
    for event, elem in xml_iter:
        if event == 'start':
            if elem.tag == 'sentence' and elem.tag != '' and current_sentence != elem.attrib['id']:
                    current_sentence = elem.attrib['id']
                    annotations.append({'id': current_sentence, 'ann': []})

            if elem.tag == 'orth' and elem.tag != '':
                ann_id += 1
                current_orth = elem.text

            if elem.tag == 'base' and elem.tag != '':
                    current_base = elem.text

            if elem.tag == 'ann' and elem.attrib['chan'] in attributes[model].values() and elem.text != '0':
                item = {'id': ann_id,
                        'orth': current_orth,
                        'base': current_base,
                        'chan': elem.attrib['chan'],
                        'chan_val': elem.text,
                        'locations': []
                        }
                i = next(item for item in annotations if item["id"] == current_sentence)
                i.get('ann').append(item)

    remove_empty_annotations(annotations)
    combine_channels(annotations)
    return annotations


def combine_channels(annotations):
    grouper = itemgetter("chan", "chan_val")
    for i in annotations:
        if len(i['ann']) > 1:
            for key, group in itertools.groupby(sorted(i['ann'], key=grouper), grouper):
                sublist = list(group)
                if len(sublist) > 1:
                    base = ''
                    orth = ''
                    for b in sublist:
                        base += b['base']+' '
                        orth += b['orth']+' '
                        i['ann'].remove(b)

                    combined = sublist[0]
                    combined['orth'] = orth.strip()
                    combined['base'] = base.strip()
                    i['ann'].append(combined)


def remove_empty_annotations(annotations):
    items_to_remove = []

    for i in annotations:
        if not i['ann']:
            items_to_remove.append(i)

    for i in items_to_remove:
        annotations.remove(i)
