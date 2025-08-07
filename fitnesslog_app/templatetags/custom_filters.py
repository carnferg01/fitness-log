from django import template

register = template.Library()

def get_contrast_color(hex_color):
    """
    Return 'black' or 'white' depending on which offers better contrast with the background color.
    Uses W3C luminance and contrast ratio formula.
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return 'black'  # fallback

    # Convert hex to RGB
    r, g, b = [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]

    # Convert to linear luminance
    def lum(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    L = 0.2126 * lum(r) + 0.7152 * lum(g) + 0.0722 * lum(b)

    # Contrast ratios with black and white text
    contrast_white = (1.05) / (L + 0.05)
    contrast_black = (L + 0.05) / 0.05

    return 'white' if contrast_white > contrast_black else 'black'


@register.filter
def contrast_text(hex_color):
    return get_contrast_color(hex_color)



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')


@register.filter
def activity_placeholder(vm, field_name):
    """Try to get a value from vm._activity to use as placeholder."""
    try:
        val = getattr(vm._activity, field_name)
        return val if val not in [None, ''] else ''
    except AttributeError:
        return ''