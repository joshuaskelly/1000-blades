import errno
import glob
import json
import os
import random

import numpy
import tracery
from tracery.modifiers import base_english

from PIL import Image

from extended_english import extended_english

def calculate_image_possibilities():
    """Computes the total possible combinations for sword pieces

    Returns:
        The total number of unique combinations of sword pieces
    """

    # Reordering the color ramps in the palette yields 3! combinations
    palette_reorder_possibilities = 6

    return len(palettes) * palette_reorder_possibilities * len(grips) * len(pommels) * len(crossguards) * len(blades)


def print_possibility_space():
    """Displays the total combinations of various proc gen items."""

    print("Possibility space:")
    print("   {} unique sword images".format(calculate_image_possibilities()))


def generate_sword_image():
    """Generates a sword image from pieces

    Returns:
        A PIL Image object.
    """

    # Chose a random set of pieces
    palette = Image.open(random.choice(palettes), 'r')
    grip = Image.open(random.choice(grips), 'r')
    pommel = Image.open(random.choice(pommels), 'r')
    crossguard = Image.open(random.choice(crossguards), 'r')
    blade = Image.open(random.choice(blades), 'r')

    # Small chance to reorder palette
    primary_palette = palette.palette.palette[0:15]
    secondary_palette = palette.palette.palette[15:30]
    accent_palette = palette.palette.palette[30:45]
    transparency = palette.palette.palette[45:]

    p = primary_palette + secondary_palette + accent_palette + transparency

    if random.random() > 0.95:
        reordered_palettes = [
            primary_palette + accent_palette + secondary_palette + transparency,
            secondary_palette + primary_palette + accent_palette + transparency,
            secondary_palette + accent_palette + primary_palette + transparency,
            accent_palette + primary_palette + secondary_palette + transparency,
            accent_palette + secondary_palette + primary_palette + transparency
        ]

        p = random.choice(reordered_palettes)

    # Apply palette
    for image in (grip, pommel, crossguard, blade):
        image.putpalette(p)

    composite = Image.new('RGBA', (32, 32))

    # Paste with mask needs to be RGBA data. Convert() is used to accomplish this.
    composite.paste(grip)
    composite.paste(pommel, (0, 0), pommel.convert())
    composite.paste(blade, (0, 0), blade.convert())
    composite.paste(crossguard, (0, 0), crossguard.convert())

    return composite


def generate_sword_data(index):
    """Generates sword JSON data

    Returns:
        Sword data as dict
    """
    with open('./json/sword.json') as file:
        sword_data = json.loads(file.read())

    with open('./json/names.json') as file:
        name_rules = json.loads(file.read())

    name_grammar = tracery.Grammar(name_rules)
    name_grammar.add_modifiers(base_english)
    name_grammar.add_modifiers(extended_english)

    sword_data['name'] = f'Blade {index + 1}:\n{name_grammar.flatten("#root#")}'
    sword_data['tex'] = index
    sword_data['brokenTex'] = index
    sword_data['spriteAtlas'] = 'blades'
    sword_data['baseDamage'] = int(numpy.random.normal(10, 4))
    sword_data['randDamage'] = int(numpy.random.normal(10, 4))
    sword_data['durability'] = int(numpy.random.normal(100, 40))
    sword_data['knockback'] = numpy.random.normal(0.15, 0.025)
    sword_data['reach'] = numpy.random.normal(0.5, 0.125) + 0.25
    sword_data['speed'] = ((1 - (sword_data['baseDamage'] + sword_data['randDamage']) / 44) * 2.0) + 0.25
    sword_data['damageType'] = numpy.random.choice(
        [
            'PHYSICAL',
            'MAGIC',
            'FIRE',
            'ICE',
            'LIGHTNING',
            'POISON',
            'HEALING',
            'PARALYZE',
            'VAMPIRE'
        ],
        p=[
            0.5,
            0.1,
            0.1,
            0.1,
            0.1,
            0.04,
            0.0,
            0.03,
            0.03
        ]
    )
    sword_data['shader'] = {
        'PHYSICAL': None,
        'MAGIC': 'magic-item-purple',
        'FIRE': 'magic-item-red',
        'ICE': 'magic-item',
        'LIGHTNING': 'magic-item-white',
        'POISON': 'magic-item-green',
        'HEALING': 'magic-item',
        'PARALYZE': 'magic-item',
        'VAMPIRE': 'magic-item-red'
    }[sword_data['damageType']]
    sword_data['attackAnimation'] = numpy.random.choice(
        [
            'swordAttack',
            'swordAttackSlow',
            'daggerAttack',
            'maceAttack'
        ],
        p=[
            0.4,
            0.2,
            0.35,
            0.05
        ]
    )
    sword_data['attackStrongAnimation'] = numpy.random.choice(
        [
            'swordAttackStrong',
            'thrustAttack',
            'daggerAttackStrong',
            'maceAttackStrong'
        ],
        p=[
            0.4,
            0.2,
            0.35,
            0.05
        ]
    )
    sword_data['chargeAnimation'] = numpy.random.choice(
        [
            'swordCharge',
            'thrustCharge',
            'daggerCharge',
            'maceCharge'
        ],
        p=[
            0.35,
            0.2,
            0.35,
            0.1
        ]
    )

    return sword_data


def create_directory_structure():
    """Generates the output mod directory structure

    Raises:
        If fails to create directory
    """

    def ensure_directory(path):
        try:
            os.makedirs(path)

        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    ensure_directory('./out/textures')
    ensure_directory('./out/data')


if __name__ == "__main__":
    print("Generating blades...")

    # Create mod directory structure
    create_directory_structure()

    # Set the random seed to have deterministic results.
    random.seed('teddybear')
    numpy.random.seed(8888888)

    # Load up individual pieces
    palettes = [os.path.normpath(g) for g in glob.glob('./images/palettes/*.png')]
    grips = [os.path.normpath(g) for g in glob.glob('./images/grips/*.png')]
    pommels = [os.path.normpath(g) for g in glob.glob('./images/pommels/*.png')]
    crossguards = [os.path.normpath(g) for g in glob.glob('./images/crossguards/*.png')]
    blades = [os.path.normpath(g) for g in glob.glob('./images/blades/*.png')]

    print_possibility_space()

    sheet_size = 32 * 16, 32 * 64
    sprite_sheet = Image.new('RGBA', sheet_size)

    with open('./json/items.json') as file:
        sword_definitions = json.loads(file.read())

    # Build the sprite sheet
    for y in range(0, sheet_size[1], 32):
        for x in range(0, sheet_size[0], 32):
            index = y // 32 * sheet_size[0] // 32 + x // 32
            image = generate_sword_image()
            sprite_sheet.paste(image, (x, y))

            s = generate_sword_data(index)
            sword_definitions['unique'].append(s)

    # Save the sprite sheet to file
    sprite_sheet.save('./out/textures/blades.png')

    # Save the item definitions to file
    with open('./out/data/items.dat', 'w') as file:
        file.write(json.dumps(sword_definitions, indent=4))

    # Save the sprite sheet definition
    with open('./out/data/spritesheets.dat', 'w') as file, open('./json/spritesheets.json') as json_data:
        data = json.loads(json_data.read())
        data[0]['columns'] = sheet_size[0] / 32
        file.write(json.dumps(data, indent=4))

    print("Done!")
