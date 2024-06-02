import re

def replace_misheard_colors(text):
    # Define the colors to look for
    colors = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'pink', 'purple', 'orange', 'brown', 'grey']
    
    # Create a regex pattern to find adjacent colors separated by a space
    color_pattern = r'\b({})\s+({})\b'.format('|'.join(colors), '|'.join(colors))
    
    def replace_white(match):
        color1, color2 = match.groups()
        if (color1 == 'black' and color2 == 'white'):
            return match.group(0).replace('white', 'light')
        return match.group(0)
    
    # Use re.sub with the custom replace function
    result = re.sub(color_pattern, replace_white, text)
    
    return result