
def compare_models(locations):

    n82 = locations['n82']
    top9 = locations['top9']
    for t9 in top9:

        n82_sentence = list(filter(lambda x: x.get('id') == t9['id'], n82))

        if n82_sentence:
            for a in t9['ann']:
                n82_a = list(filter(lambda x: x.get('id') == a['id'], n82_sentence[0]['ann']))
                if n82_a:
                    if a['chan'] in n82_a[0]['chan']:
                        a['chan'] = n82_a[0]['chan']
    return top9

