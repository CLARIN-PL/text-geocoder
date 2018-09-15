from xml.etree import ElementTree

xml_iter = ElementTree.iterparse('1100979a-8ec0-4275-a29b-b3172df5c65c.ccl', events=('start', 'end'))
for event, elem in xml_iter:
    if event == 'start':
        if elem.tag == 'base':
            text = elem.text
            if text != '':
                print(text+'\n', end='')


