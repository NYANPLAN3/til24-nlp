import pkgutil
import re

data = pkgutil.get_data(__package__, 'colors.txt')
COLORS = [w.strip() for w in data.decode('utf-8').strip().split('\n')]


def replace_misheard_colors(text):
    # Define the colors to look for

    # NOTE: changed to handle specifically white
    # Create a regex pattern to find adjacent colors separated by a space
    color_pattern = r'\b({})\s+white\b'.format('|'.join(COLORS))

    def replace_white(match):
        return match.group(0).replace('white', 'light')

    # Use re.sub with the custom replace function
    result = re.sub(color_pattern, replace_white, text)

    return result
