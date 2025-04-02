import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
import pandas as pd
import matplotlib.pyplot as plt


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.time_period = 21  # default value of 21 days
        self.site_id = '04119070'  # default station choice
        self.sample_interval = 6  # default sampling interval

    def initUI(self):
        self.setGeometry(300, 300, 360, 250)  # Increased height to fit new dropdown
        self.setWindowTitle('River Data Downloader')

        self.site_id = ''

        self.combo_site = QComboBox(self)
        self.combo_site.addItem('Grand River - Wilson Ave Bridge')
        self.combo_site.addItem('Grand River - Downtown GR')
        self.combo_site.move(50, 50)
        self.combo_site.currentTextChanged.connect(self.updateSiteId)

        # Add sampling interval dropdown
        self.combo_sample = QComboBox(self)
        self.combo_sample.addItems(['1 hour', '2 hours', '3 hours'])
        self.combo_sample.move(130, 80)
        self.combo_sample.setCurrentText('3 hours')  # Default value
        self.combo_sample.currentTextChanged.connect(self.updateSampleInterval)

        # Add slider for time period
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(5)
        self.slider.setMaximum(21)
        self.slider.setValue(21)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setFixedWidth(200)
        self.slider.move(50, 130)  # Moved down to accommodate sampling dropdown
        self.slider.valueChanged.connect(self.updateTimePeriod)

        # Add label to display selected days
        self.time_label = QLabel('21 days', self)
        self.time_label.move(265, 130)  # Moved down

        self.button = QPushButton('Download and Display Data', self)
        self.button.move(75, 180)  # Moved down
        self.button.clicked.connect(self.downloadAndDisplayData)

        self.show()

    def updateSiteId(self, text):
        if text == 'Grand River - Wilson Ave Bridge':
            self.site_id = '04119070'
        elif text == 'Grand River - Downtown GR':
            self.site_id = '04119000'

    def updateTimePeriod(self, value):
        self.time_period = value
        self.time_label.setText(f'{value} days')

    def updateSampleInterval(self, text):
        """Update the sampling interval based on dropdown selection."""
        self.sample_interval = int(text.split()[0])  # Extract number from "X hours"

    def downloadAndDisplayData(self):
        download_river_data(self.site_id, self.time_period)
        display_river_data(self.site_id, self.sample_interval)

'''
Function: download_river_data
Inputs: river station ID, number of days of data to download
Outputs: None
Description: Downloads data for a selected river station from the USGS API. The data is saved locally into 
a file named river_level_data.rdb
'''
def download_river_data(station_id, num_days):
    # Get current date and time
    current_datetime = datetime.now()

    # Calculate date `num_days` ago
    start_datetime = current_datetime - timedelta(days=num_days)

    # Format dates as required by the USGS API
    start_dt = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '-04:00'
    end_dt = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '-04:00'

    # Construct query parameters dictionary
    params = {
        'sites': station_id,
        'agencyCd': 'USGS',  # Added this parameter
        'parameterCd': '00065',
        'startDT': start_dt,
        'endDT': end_dt,
        'format': 'rdb'
    }

    # Build the URL
    base_url = 'https://waterservices.usgs.gov/nwis/iv/'
    url = base_url + '?' + urlencode(params)

    print(f"Generated URL: {url}")  # Print the URL for debugging

    # Download the data
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the data to a file
        with open('river_level_data.rdb', 'wb') as f:
            f.write(response.content)
        print('Data downloaded and saved successfully!')
    else:
        print(f'Failed to download data: {response.status_code}')
        print(f'Response content: {response.text}')  # Print error details

'''
Function: display_river_data
Inputs: river station ID, sampling interval
Outputs: None
Description: Loads, samples data based on the sampling interval, 
and displays the river data for a selected river station.
'''
def display_river_data(station_id, sample_interval):
    # Read the RDB file into a DataFrame
    df = pd.read_csv('river_level_data.rdb', delimiter='\t', comment='#')
    df = df.rename(columns={df.columns[4]: 'level'})

    # Extract the time from the 'datetime' column as a string
    time = df['datetime'].str[11:]

    # Generate sampling times based on selected interval
    sample_hours = [f'{hour:02d}:00' for hour in range(0, 24, sample_interval)]
    df_sampled = df[time.isin(sample_hours)]
    
    # Convert level values from string to numeric
    df_sampled = df_sampled.astype({'level': float}, errors='ignore')
    df_sampled.iloc[0, 4] = df_sampled.iloc[1, 4]  # overwrite '14n' string

    fig, ax1 = plt.subplots(figsize=(12, 8))
    ax1.plot(df_sampled['datetime'], df_sampled['level'])
    ax1.set_xlabel(f'Date ({sample_interval} hr Increments)')
    ax1.set_ylabel('River Level (feet)')

    if station_id == '04119000':
        plt.title('Grand River at Grand Rapids, MI - 04119000')
    elif station_id == '04119070':
        plt.title('Grand River at State Hwy M-11 at Grandville, MI - 04119070')

    ax1.tick_params(rotation=45)
    # Adjust x-tick frequency based on sampling interval
    tick_step = max(24 // sample_interval, 1)  # Show at least one label per day
    ax1.set_xticks(ax1.get_xticks()[::tick_step])
    plt.tight_layout()
    plt.show()




if __name__ == '__main__':
    app = QApplication(sys.argv)  # execute PyQt5 widget
    ex = MyApp()
    sys.exit(app.exec_())