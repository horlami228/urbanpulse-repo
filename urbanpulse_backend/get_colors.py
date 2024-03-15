def get_color(score):
    if score > 0.66:  
        return 'green'
    elif score > 0.33:
        return 'orange'
    else:
        return 'red'
    