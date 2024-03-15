import time
import folium
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def create_folium_map():
    # Create a map centered around Japan
    japan_center = [36.2048, 138.2529]
    flight_map = folium.Map(
        location=japan_center, zoom_start=5, tiles="Cartodb dark_matter"
    )

    return flight_map


class ScreenMapping:

    def print_map(file_paths, web_engine_view):

        for filename in file_paths:
            if filename.endswith(".csv"):
                df = pd.read_csv(
                    filename,
                    delimiter=",",
                    header=None,
                    names=[
                        "Time",
                        "Flight",
                        "Latitude",
                        "Longitude",
                        "Altitude",
                        "Flight Type",
                        "Depart",
                        "Arrival",
                    ],
                )

        # Convert the extracted string to the desired date format '13-03-2021'
        df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S.%f")
        geometry = [
            Point(lon, lat) for lon, lat in zip(df["Longitude"], df["Latitude"])
        ]
        df.sort_values(
            by=["Flight", "Flight Type", "Depart", "Arrival"], ascending=True
        )
        gdf = gpd.GeoDataFrame(df, geometry=geometry)
        gdf[:30]
        unique_flights = df["Flight"].unique().tolist()

        time_interval = 5
        flight_map = create_folium_map()

        # Define a list of colors for different flights
        line_colors = ["blue", "red", "green", "purple", "orange", "brown"]

        # Create a time counter DivIcon
        time_counter_div = folium.DivIcon(
            html="<div id='time_counter'>Time Counter: </div>", icon_size=(200, 40)
        )

        # Add the time counter DivIcon to the map using a Marker
        folium.Marker(
            location=(35, 135),  # Adjust the location for the time counter
            icon=time_counter_div,
        ).add_to(flight_map)

        # Iterate through time intervals
        for time_index in range(0, len(gdf), time_interval):

            flight_map = create_folium_map()

            # Add lines to connect the points in the trajectory
            for i, flight_id in enumerate(unique_flights):
                subset_gdf = gdf.loc[gdf["Flight"] == flight_id].iloc[: time_index + 1]

                # Extract Point geometries from the 'geometry' column
                points = [(point.y, point.x) for point in subset_gdf["geometry"]]

                # Add dotted lines to connect consecutive points
                if len(points) > 1:
                    folium.PolyLine(
                        locations=points,
                        color=line_colors[i % len(line_colors)],
                        weight=2,
                        opacity=0.8,
                        dash_array="5, 5",
                    ).add_to(flight_map)

                # Add the latest point as a marker
                latest_point = subset_gdf.iloc[-1]
                lat, lon = latest_point["geometry"].y, latest_point["geometry"].x

                # Details for the tooltip
                tooltip_text = (
                    f"<strong>Flight:</strong> {latest_point['Flight']}<br>"
                    f"<strong>Flight Type:</strong> {latest_point['Flight Type']}<br>"
                    f"<strong>Depart:</strong> {latest_point['Depart']}<br>"
                    f"<strong>Arrival:</strong> {latest_point['Arrival']}<br>"
                    f"<strong>Latitude:</strong> {latest_point['Latitude']}<br>"
                    f"<strong>Longitude:</strong> {latest_point['Longitude']}"
                )

                folium.CircleMarker(
                    location=(lat, lon),
                    radius=5,
                    color="white",
                    tooltip=folium.Tooltip(tooltip_text, sticky=True),
                    fill_color=line_colors[i % len(line_colors)],
                    fill_opacity=0.5,
                ).add_to(flight_map)

            # Update the time counter
            time_counter_div.options["html"] = (
                "<div id='time_counter'>Time Counter: "
                + gdf.iloc[time_index]["Time"].strftime("%H:%M:%S.%f")
                + "</div>"
            )

            # Display the updated map
            web_engine_view.setHtml(flight_map._repr_html_())

            # Pause for the specified time interval
            time.sleep(time_interval)
            break

