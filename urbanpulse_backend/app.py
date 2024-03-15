from flask import Flask, render_template, request
import folium
import geopandas as gpd
import numpy as np
from assign_scores import assign_score
from get_color_and_tooltip import get_color_and_tooltip

app = Flask(__name__)

"""IMPORT ALL GEOGRAPHICAL DATA IN GEOJSON FORM"""
# Transportation
ev_charging_stations_gdf = gpd.read_file("./geojson_data/EV_Charging_Stations.geojson")
# Services
fire_stations_gdf = gpd.read_file("./geojson_data/BFES_Fire_Stations.geojson")
hospital_gdf = gpd.read_file("./geojson_data/Hospitals.geojson")
schools_gdf = gpd.read_file("./geojson_data/Schools.geojson")
transit_gdf = gpd.read_file("./geojson_data/Transit.geojson")



# Land Use
registered_plan_gdf = gpd.read_file("./geojson_data/Registered_Plan_of_Subdivision.geojson")
official_plan_gdf = gpd.read_file("./geojson_data/Official_Plan_Schedule_A%3A_General_Land_Use.geojson")
future_condo_development = gpd.read_file("./geojson_data/Draft_Plan_of_Condominium.geojson")

# Zoning
heritage_properties_gdf = gpd.read_file("./geojson_data/Heritage_Properties.geojson")

Underutilized_Addresses = gpd.read_file("./geojson_data/Underutilized_Addresses.geojson")

Underutilized_Addresses['LOCATION'] = Underutilized_Addresses.apply(lambda row: row['FULL_ADDRESS'] if row['LOCATION'] == 'Occupied' else row['LOCATION'], axis=1)


# Combine all transportation-related points into a single GeoDataFrame
transportation_gdf = gpd.overlay(ev_charging_stations_gdf, how='union')


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


# This UrbanPulse full logic
def Brampton(location):
    # First try to find the location in ranked_condo_plans_gdf
    Location = ranked_condo_plans_gdf[ranked_condo_plans_gdf['LOCATION'] == location]
    
    # If not found in the first dataset, try the second
    if Location.empty:
        Location = ranked_Underutilized_Addresses[ranked_Underutilized_Addresses['LOCATION'] == location]
    
    # Continue with the location processing
    if not Location.empty:
        centroid = Location.geometry.centroid.iloc[0]
        map_location = [centroid.y, centroid.x]
    else:
        # Default location if not found in both datasets
        map_location = [43.7315, -79.7624]

    map = folium.Map(location=map_location, zoom_start=15)
    if location is None:
        return map
    
    # Check if the 'score' column exists and process accordingly
    if 'score' in Location.columns and not Location['score'].empty:
        max_score = Location['score'].max()
        Location['normalized_score'] = Location['score'] / max_score
        Location['color'], Location['tooltip_message'] = zip(*Location['normalized_score'].apply(get_color_and_tooltip))
    
    for _, loc in Location.iterrows():
        if 'geometry' in loc and loc['geometry']:
            if loc['geometry'].geom_type == 'Point':
                location_point = [loc['geometry'].y, loc['geometry'].x]
            else:  # For Polygon/MultiPolygon geometries, use the centroid
                location_point = [loc['geometry'].centroid.y, loc['geometry'].centroid.x]
            
            folium.Marker(
                location=location_point,
                icon=folium.Icon(color=loc['color'] if 'color' in loc else 'blue'),
                tooltip=folium.Tooltip(loc['tooltip_message'] if 'tooltip_message' in loc else 'No additional info')
            ).add_to(map)
    
    return map

# endpoint definition
@app.route("/map", methods=["GET"], strict_slashes=False)
def get_folioum_map():
    """Return the map HTML."""
    location = request.args.get('location')
    map_html = Brampton(location=location)._repr_html_()
    return render_template('map.html', map_html=map_html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
