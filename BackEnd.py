import sys
import folium
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets


def create_folium_map():
    # Create a map centered around Japan
    japan_center = [36.2048, 138.2529]
    flight_map = folium.Map(
        location=japan_center, zoom_start=5, tiles="Cartodb dark_matter"
    )

    return flight_map


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
        label1.setStyleSheet("font: bold 12px;")
        right_layout.addWidget(label1, alignment=QtCore.Qt.AlignHCenter)

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
        right_layout.addWidget(button3)

        # Stop button
        button4 = QtWidgets.QPushButton("Stop")
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
        listbox = QtWidgets.QTreeWidget()
        listbox.setHeaderLabels(["Time"])
        for time in time_data:
            item = QtWidgets.QTreeWidgetItem([time])
            listbox.addTopLevelItem(item)
        right_layout.addWidget(listbox)

        # Insert spacing
        right_layout.addSpacing(20)

        # Radio buttons for Mode
        label_mode = QtWidgets.QLabel("Mode")
        right_layout.addWidget(label_mode)

        mode_button_group = QtWidgets.QButtonGroup()
        for text, value in [("Dynamic", "Dynamic"), ("Static", "Static")]:
            radio = QtWidgets.QRadioButton(text)
            radio.setChecked(value == "Dynamic")
            right_layout.addWidget(radio)
            mode_button_group.addButton(radio)

        # Integrate Folium map widget to the left_layout
        self.flight_map = create_folium_map()
        self.web_engine_view = QtWebEngineWidgets.QWebEngineView()
        self.web_engine_view.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )

        # Add the widget to the layout and set stretch factors
        left_layout.addWidget(self.web_engine_view, stretch=1)
        # Set alignment to fill the available space
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(QtCore.Qt.AlignTop)

    def open_action(self):
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames()
        print("Selected files:", file_paths)
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
                self.update_canvas_left(df)

    def update_canvas_left(self, df):

        # Add markers for flights
        flights_data = [
            {
                "Time": "00:11:58.1",
                "Flight": "JN00012",
                "Latitude": 33.068832,
                "Longitude": 128.953271,
            },
            {
                "Time": "00:11:58.1",
                "Flight": "JN00013",
                "Latitude": 25.293022,
                "Longitude": 127.561049,
            },
            {
                "Time": "00:11:58.6",
                "Flight": "JN00014",
                "Latitude": 33.147860,
                "Longitude": 129.221991,
            },
            {
                "Time": "00:11:58.6",
                "Flight": "JN00024",
                "Latitude": 34.301537,
                "Longitude": 133.520316,
            },
            {
                "Time": "00:11:59.1",
                "Flight": "JN00006",
                "Latitude": 33.289685,
                "Longitude": 130.328418,
            },
        ]

        for flight in flights_data:
            folium.Marker(
                location=[flight["Latitude"], flight["Longitude"]],
                popup=f"{flight['Flight']} - {flight['Time']}",
                icon=folium.Icon(color="blue", icon="plane"),
            ).add_to(self.flight_map)
            # Details for the tooltip
            tooltip_text = (
                f"<strong>Flight:</strong> {flight['Flight']}<br>"
                f"<strong>Latitude:</strong> {flight['Latitude']}<br>"
                f"<strong>Longitude:</strong> {flight['Longitude']}"
            )

            folium.CircleMarker(
                location=[flight["Latitude"], flight["Longitude"]],
                radius=5,
                color="white",
                tooltip=folium.Tooltip(tooltip_text, sticky=True),
                fill_opacity=0.5,
            ).add_to(self.flight_map)

        self.web_engine_view.setHtml(self.flight_map._repr_html_())

    def exit_action(self):
        QtWidgets.qApp.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
