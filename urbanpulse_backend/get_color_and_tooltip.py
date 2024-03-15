def get_color_and_tooltip(score):
    if score > 0.66:
        return ('green', 'Highly suitable for development: optimal location with strong potential for residential projects')
    elif score > 0.33:
        return ('orange', 'Moderately suitable for development: consider additional factors or improvements')
    else:
        return ('red', 'Limited suitability for immediate development: ideal for long-term planning or revitalization')
    