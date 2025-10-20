import PIL.Image
from typing import List

from OpenHosta import emulate

def image_of_char_grid_to_list_of_string(image: PIL.Image.Image) -> List[str]:
    """
    Convert an image of a character grid into a list of strings.
    Each string represents a row of characters.
    Rows does not have meaning. Just extract the characters as they are in the image.
    
    Arguments:
        image (PIL.Image.Image): The input image containing the character grid.
        
    Returns:
        List[str]: A list of strings. each string is a line of the grid. no space in between.
    """
    return emulate()


def demo():
    img2 = PIL.Image.open("grid.png")
    char_grid = image_of_char_grid_to_list_of_string(img2)
    for row in char_grid:
        print(row)