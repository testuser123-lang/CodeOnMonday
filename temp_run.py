import sys
import folium
import pandas as pd
import geopandas as gpd
from PyQt5.QtCore import QTimer
from PyQt5 import QtGui, QtWidgets, QtCore, QtWebEngineWidgets
from shapely.geometry import Point


class ScreenMapping:
    @staticmethod
    def print_map(gdf, unique_flights, line_colors, flight_map, time_index):
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
                    weight=1,
                    opacity=0.1,
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
                radius=8,
                color="white",
                tooltip=folium.Tooltip(tooltip_text, sticky=True),
                fill_color=line_colors[i % len(line_colors)],
                fill_opacity=0.5,
            ).add_to(flight_map)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plot Tracker")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QHBoxLayout(central_widget)

        # Left canvas
        self.canvas_left = QtWidgets.QFrame()
        self.canvas_left.setStyleSheet("background-color: blue;")

        layout.addWidget(self.canvas_left)
        left_layout = QtWidgets.QVBoxLayout(self.canvas_left)

        # Right canvas
        self.canvas_right = QtWidgets.QFrame()
        self.canvas_right.setStyleSheet("background-color: #F0F0F0;")
        self.canvas_right.setMaximumWidth(200)  # Decrease width
        self.canvas_right.setMinimumHeight(200)  # Decrease height
        layout.addWidget(self.canvas_right)

        right_layout = QtWidgets.QVBoxLayout(self.canvas_right)

        # Flight Tracker App label
        label1 = QtWidgets.QLabel("Flight Tracker App")
        label1.setStyleSheet("font: bold 14px;")
        right_layout.addWidget(label1, alignment=QtCore.Qt.AlignHCenter)

        # Logo image
        logo_image = QtWidgets.QLabel()
        logo_image.setPixmap(QtGui.QPixmap("ロゴマーク（カラー小）.jpg"))
        right_layout.addWidget(logo_image, alignment=QtCore.Qt.AlignHCenter)

        # Open button
        button1 = QtWidgets.QPushButton("Open")
        button1.clicked.connect(self.open_action)
        right_layout.addWidget(button1)

        # Exit button
        button2 = QtWidgets.QPushButton("Exit")
        button2.clicked.connect(self.exit_action)
        right_layout.addWidget(button2)

        # Start button
        button3 = QtWidgets.QPushButton("Start")
        button3.clicked.connect(self.start_action)
        right_layout.addWidget(button3)

        # Stop button
        button4 = QtWidgets.QPushButton("Stop")
        button4.clicked.connect(self.stop_action)
        right_layout.addWidget(button4)

        # Time data list
        time_data = [
            "00:30",
            "01:00",
            "01:30",
            "02:00",
            "02:30",
            "03:00",
            "03:30",
            "04:00",
            "04:30",
            "05:00",
            "05:30",
            "06:00",
            "06:30",
            "07:00",
            "07:30",
            "08:00",
            "08:30",
            "09:00",
            "09:30",
            "10:00",
            "10:30",
            "11:00",
            "11:30",
            "12:00",
            "12:30",
            "13:00",
            "13:30",
            "14:00",
            "14:30",
            "15:00",
            "15:30",
            "16:00",
            "16:30",
            "17:00",
            "17:30",
            "18:00",
            "18:30",
            "19:00",
            "19:30",
            "20:00",
            "20:30",
            "21:00",
            "21:30",
            "22:00",
            "22:30",
            "23:00",
            "23:30",
        ]

        # List box
        self.listbox = QtWidgets.QTreeWidget()
        self.listbox.setHeaderLabels(["Time"])
        for time_item in time_data:
            item = QtWidgets.QTreeWidgetItem([time_item])
            self.listbox.addTopLevelItem(item)
        right_layout.addWidget(self.listbox)

        # Insert spacing
        right_layout.addSpacing(20)

        # Radio buttons for Mode
        label_mode = QtWidgets.QLabel("Mode")
        right_layout.addWidget(label_mode)

        self.mode_button_group = QtWidgets.QButtonGroup()
        for text, value in [("Dynamic", "Dynamic"), ("Static", "Static")]:
            radio = QtWidgets.QRadioButton(text)
            radio.setChecked(value == "Dynamic")
            right_layout.addWidget(radio)
            self.mode_button_group.addButton(radio)

        # Integrate Folium map widget to the left_layout
        self.web_engine_view = QtWebEngineWidgets.QWebEngineView()
        self.web_engine_view.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )

        # Add the widget to the layout and set stretch factors
        left_layout.addWidget(self.web_engine_view, stretch=1)
        # Set alignment to fill the available space
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(QtCore.Qt.AlignTop)

        self.timer = QTimer(self)
        self.time_index = 0

    def open_action(self):
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames()

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
        self.gdf = gpd.GeoDataFrame(df, geometry=geometry)
        self.unique_flights = df["Flight"].unique().tolist()

        self.time_interval = 10000
        self.flight_map = self.create_folium_map()

        # Define a list of colors for different flights
        self.line_colors = ["blue", "red", "green", "purple", "orange", "brown"]

        self.timer.timeout.connect(self.update_map)
        self.timer.start(self.time_interval)

    def create_folium_map(self):
        # Create a map centered around Japan
        japan_center = [36.2048, 138.2529]
        flight_map = folium.Map(
            location=japan_center, zoom_start=5, tiles="Cartodb dark_matter"
        )

        return flight_map

    def update_map(self):
        time_item = self.listbox.topLevelItem(self.time_index)
        time_text = time_item.text(0)

        self.flight_map = self.create_folium_map()

        ScreenMapping.print_map(
            self.gdf,
            self.unique_flights,
            self.line_colors,
            self.flight_map,
            self.time_index,
        )

        self.web_engine_view.setHtml(self.flight_map._repr_html_())

        self.time_index = (self.time_index + 1) % self.listbox.topLevelItemCount()

    def exit_action(self):
        QtWidgets.qApp.quit()

    def start_action(self):
        self.timer.start(self.time_interval)

    def stop_action(self):
        self.timer.stop()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
