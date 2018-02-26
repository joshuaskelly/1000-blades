def possesive(text, *params):
    if text[-1] in 's':
        return f'{text}'

    return f'{text}\'s'


def er(text, *params):
    if text[-3:] == 'ate':
        return f'{text[:-1]}or'

    if text[-1] in 'e':
        return f'{text}r'

    if text[-1] in 'bnpt':
        return f'{text}{text[-1:]}er'

    return f'{text}er'

def ing(text, *params):
    if text[-1] in 'ey':
        return f'{text[:-1]}ing'
    return f'{text}ing'

extended_english = {
    'possesive': possesive,
    'er': er,
    'ing': ing
}
