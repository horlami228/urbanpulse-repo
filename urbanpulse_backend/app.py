from flask import Flask, render_template, request
import folium
import geopandas as gpd
import numpy as np
from assign_scores import assign_score
from get_colors import get_color

app = Flask(__name__)

"""IMPORT ALL GEOGRAPHICAL DATA IN GEOJSON FORM"""
# Transportation
ev_charging_stations_gdf = gpd.read_file("C:\\Users\\USER\\Downloads\\EV_Charging_Stations.geojson")
# Services
fire_stations_gdf = gpd.read_file("C:\\Users\\USER\\Downloads\\BFES_Fire_Stations.geojson")
hospital_gdf = gpd.read_file("C:\\Users\\USER\\Downloads\\Hospitals.geojson")
schools_gdf = gpd.read_file("C:\\Users\\USER\\Downloads\\Schools.geojson")
transit_gdf = gpd.read_file("C:\\Users\\USER\\Downloads\\Transit.geojson")


# Land Use
registered_plan_gdf = gpd.read_file("C:\\Users\\USER\\Downloads\\Registered_Plan_of_Subdivision.geojson")
official_plan_gdf = gpd.read_file("C:\\Users\\USER\\Downloads\\Official_Plan_Schedule_A%3A_General_Land_Use.geojson")
future_condo_development = gpd.read_file("C:\\Users\\USER\\Downloads\\Draft_Plan_of_Condominium.geojson")

# Zoning
heritage_properties_gdf = gpd.read_file("C:\\Users\\USER\\Downloads\\Heritage_Properties.geojson")

Underutilized_Addresses = gpd.read_file("C:\\Users\\USER\\Downloads\\Underutilized_Addresses.geojson")

Underutilized_Addresses['LOCATION'] = Underutilized_Addresses.apply(lambda row: row['FULL_ADDRESS'] if row['LOCATION'] == 'Occupied' else row['LOCATION'], axis=1)


# Combine all transportation-related points into a single GeoDataFrame
transportation_gdf = gpd.overlay(ev_charging_stations_gdf, streets_centreline_gdf, how='union')


"""CONDO PLANS"""
# Define the ranges for each amenity type ([max distance, points])
transit_ranges = [(400, 10), (800, 5)]
fire_station_ranges = [(800, 10), (1200, 5)]
ev_charging_ranges = [(1000, 10), (1200, 5)]
school_ranges = [(800, 10), (1100, 5)]
hospital_ranges = [(5000, 10), (8000, 5)]

# Initialize the score column
future_condo_development['score'] = 0

# Calculate the distance to the nearest amenity and update the score accordingly
for idx, condo in future_condo_development.iterrows():
    # Transit
    min_distance_transit = np.min([condo.geometry.distance(point) for point in transit_gdf.geometry]) * 100000  # Adjust the unit based on your CRS
    future_condo_development.at[idx, 'score'] += assign_score(min_distance_transit, transit_ranges)
    
    # Fire Station
    min_distance_fire_station = np.min([condo.geometry.distance(point) for point in fire_stations_gdf.geometry]) * 100000
    future_condo_development.at[idx, 'score'] += assign_score(min_distance_fire_station, fire_station_ranges)
    
    # EV Charging
    min_distance_ev_charging = np.min([condo.geometry.distance(point) for point in ev_charging_stations_gdf.geometry]) * 100000
    future_condo_development.at[idx, 'score'] += assign_score(min_distance_ev_charging, ev_charging_ranges)
    
    # School
    min_distance_school = np.min([condo.geometry.distance(point) for point in schools_gdf.geometry]) * 100000
    future_condo_development.at[idx, 'score'] += assign_score(min_distance_school, school_ranges)
    
    # Hospital
    min_distance_hospital = np.min([condo.geometry.distance(point) for point in hospital_gdf.geometry]) * 100000
    future_condo_development.at[idx, 'score'] += assign_score(min_distance_hospital, hospital_ranges)

# Now, future_condo_development will have an updated 'score' column reflecting the detailed proximity scoring
# You can sort this DataFrame based on the score to rank the condominium locations
ranked_condo_plans_gdf = future_condo_development.sort_values(by='score', ascending=False)

"""UNDER UTILIZED ADDRESSES IN BRAMPTON"""
# Initialize the score column
Underutilized_Addresses['score'] = 0

# Calculate the distance to the nearest amenity and update the score accordingly
for idx, Addresses in Underutilized_Addresses.iterrows():
    # Transit
    min_distance_transit = np.min([Addresses.geometry.distance(point) for point in transit_gdf.geometry]) * 100000  # Adjust the unit based on your CRS
    Underutilized_Addresses.at[idx, 'score'] += assign_score(min_distance_transit, transit_ranges)
    
    # Fire Station
    min_distance_fire_station = np.min([Addresses.geometry.distance(point) for point in fire_stations_gdf.geometry]) * 100000
    Underutilized_Addresses.at[idx, 'score'] += assign_score(min_distance_fire_station, fire_station_ranges)
    
    # EV Charging
    min_distance_ev_charging = np.min([Addresses.geometry.distance(point) for point in ev_charging_stations_gdf.geometry]) * 100000
    Underutilized_Addresses.at[idx, 'score'] += assign_score(min_distance_ev_charging, ev_charging_ranges)
    
    # School
    min_distance_school = np.min([Addresses.geometry.distance(point) for point in schools_gdf.geometry]) * 100000
    Underutilized_Addresses.at[idx, 'score'] += assign_score(min_distance_school, school_ranges)
    
    # Hospital
    min_distance_hospital = np.min([Addresses.geometry.distance(point) for point in hospital_gdf.geometry]) * 100000
    Underutilized_Addresses.at[idx, 'score'] += assign_score(min_distance_hospital, hospital_ranges)

# Now, future_condo_development will have an updated 'score' column reflecting the detailed proximity scoring
# You can sort this DataFrame based on the score to rank the condominium locations
ranked_Underutilized_Addresses = Underutilized_Addresses.sort_values(by='score', ascending=False)


def Brampton(location):
    if location == "vacant":
        Location = ranked_Underutilized_Addresses[ranked_Underutilized_Addresses['LOCATION'] == location]
    
    Location = ranked_condo_plans_gdf[ranked_condo_plans_gdf['LOCATION'] == location]
    
    # Calculate the centroid of the selected location's geometry
    # This assumes that the geometry is a valid geometry
    # and that Location is not empty
    if not Location.empty:
        centroid = Location.geometry.centroid.iloc[0]
        map_location = [centroid.y, centroid.x]
    else:
        # Default location if no geometry is found
        map_location = [43.7315, -79.7624]
    
    # Create the map centered on the centroid of the selected location
    map = folium.Map(location=map_location, zoom_start=15)
    
    if location == None:
        return map
    
    max_score = ranked_condo_plans_gdf['score'].max()
    ranked_condo_plans_gdf['normalized_score'] = ranked_condo_plans_gdf['score'] / max_score
    Location['color'] = Location['normalized_score'].apply(get_color)
    
    if Location == "vacant":
    # Add each point to the map with color based on its normalized score
        for _, loc in Location.iterrows():
            folium.Marker(
                location=[loc['geometry'].y, loc['geometry'].x],
                icon=folium.Icon(color=get_color(loc['normalized_score'])),
                tooltip=f'Score: {loc["score"]}'
            ).add_to(map)
    
    else:
            
        for _, loc in Location.iterrows():
            folium.GeoJson(
                loc['geometry'],
                style_function=lambda x, color=loc['color']: {'fillColor': color, 'color': color},
                tooltip=f'Score: {loc["score"]}'
            ).add_to(map)
    
    return map


@app.route("/map")
def get_folioum_map():
    """Return the map HTML."""
    location = request.args.get('location')
    map_html = Brampton(location=location)._repr_html_()
    return render_template('map.html', map_html=map_html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
