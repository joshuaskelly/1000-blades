import glob
import os
import random

from PIL import Image


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


if __name__ == "__main__":
    print("Generating blades...")

    # Set the random seed to have deterministic results.
    random.seed("teddybear")

    # Load up individual pieces
    palettes = [os.path.normpath(g) for g in glob.glob('./images/palettes/*.png')]
    grips = [os.path.normpath(g) for g in glob.glob('./images/grips/*.png')]
    pommels = [os.path.normpath(g) for g in glob.glob('./images/pommels/*.png')]
    crossguards = [os.path.normpath(g) for g in glob.glob('./images/crossguards/*.png')]
    blades = [os.path.normpath(g) for g in glob.glob('./images/blades/*.png')]

    print_possibility_space()

    sheet_size = 32 * 16, 32 * 64
    sprite_sheet = Image.new('RGBA', sheet_size)

    # Build the sprite sheet
    for x in range(0, sheet_size[0], 32):
        for y in range(0, sheet_size[1], 32):
            image = generate_sword_image()
            sprite_sheet.paste(image, (x, y))

    # Save the sprite sheet to file
    sprite_sheet.save('out.png')
    print("Done!")
