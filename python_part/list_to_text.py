from OpenHosta import emulate
from PIL.Image import Image
from typing import List

def image_of_list_of_words_to_list_of_string(image: Image) -> List[str]:
    """
    Convert an image of a list of words into a list of strings.
    Each string represents a word.
    
    Arguments:
        image (PIL.Image.Image): The input image containing the list of words.
        
    Returns:
        List[str]: A list of strings. each string is a word.
    """
    return emulate()