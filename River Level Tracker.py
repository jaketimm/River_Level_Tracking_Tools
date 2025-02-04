import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
import pandas as pd
import matplotlib.pyplot as plt

Wilson_Ave_Flood_Level = 7.5  # estimated flood level in feet


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.time_period = 30  # default value of 30 days
        self.site_id = '04119070'  # default station choice

    def initUI(self):
        self.setGeometry(300, 300, 360, 200)
        self.setWindowTitle('River Data Downloader')

        self.site_id = ''

        self.combo_site = QComboBox(self)
        self.combo_site.addItem('Grand River - Wilson Ave Bridge')
        self.combo_site.addItem('Grand River - Downtown GR')
        self.combo_site.addItem('Buck Creek at Wilson Ave')
        self.combo_site.move(50, 50)

        self.combo_site.currentTextChanged.connect(self.updateSiteId)

        self.combo_time = QComboBox(self)
        self.combo_time.addItem('30 days')
        self.combo_time.addItem('7 days')
        self.combo_time.move(135, 100)

        self.combo_time.currentTextChanged.connect(self.updateTimePeriod)

        self.button = QPushButton('Download and Display Data', self)
        self.button.move(75, 150)
        self.button.clicked.connect(self.downloadAndDisplayData)

        self.show()

    def updateSiteId(self, text):  # set river station ID based on dropdown menu
        if text == 'Grand River - Wilson Ave Bridge':
            self.site_id = '04119070'
        elif text == 'Grand River - Downtown GR':
            self.site_id = '04119000'
        elif text == 'Buck Creek at Wilson Ave':
            self.site_id = '04119160'

    def updateTimePeriod(self, text):  # set time period based on dropdown menu
        if text == '30 days':
            self.time_period = 30
        elif text == '7 days':
            self.time_period = 7

    def downloadAndDisplayData(self):  # button to execute functions
        download_river_data(self.site_id, self.time_period)
        display_river_data(self.site_id)

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

    # Calculate date 30 days ago
    start_datetime = current_datetime - timedelta(days=num_days)

    # Format dates as required by the USGS API
    start_dt = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '-04:00'
    end_dt = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '-04:00'

    # Construct query parameters dictionary
    params = {
        'sites': station_id,
        'parameterCd': '00065',
        'startDT': start_dt,
        'endDT': end_dt,
        'siteStatus': 'all',
        'format': 'rdb'
    }

    # Build the URL
    base_url = 'https://waterservices.usgs.gov/nwis/iv/'
    url = base_url + '?' + urlencode(params)

    # Download the data
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the data to a file
        with open('river_level_data.rdb', 'wb') as f:
            f.write(response.content)
        print('Data downloaded and saved successfully!')
    else:
        print('Failed to download data:', response.status_code)


'''
Function: display_river_data
Inputs: river station ID
Outputs: None
Description: Loads, samples, and displays the river data for a selected river station
Increments: 7 days - 2 hr sampling. 30 days - 6 hr sampling
'''
def display_river_data(station_id):

    # Read the RDB file into a DataFrame
    df = pd.read_csv('river_level_data.rdb', delimiter='\t', comment='#')
    df = df.rename(columns={df.columns[4]: 'level'})  # rename column as it's a different number name for each station

    # Extract the time from the 'datetime' column as a string
    time = df['datetime'].str[11:]

    # Select data for every 6 hrs
    df_6h = df[time.isin(['00:00', '06:00', '12:00', '18:00'])]
    # Convert level values from string to numeric
    df_6h = df_6h.astype({'level': float}, errors='ignore')
    df_6h.iloc[0, 4] = df_6h.iloc[1, 4]  # overwrite '14n' string at beginning of level data

    fig, ax1 = plt.subplots(figsize=(12, 8))  # create a subplot and add labels
    # Plot river level data
    ax1.plot(df_6h['datetime'], df_6h['level'])
    ax1.set_xlabel('Date (6 hr Increments)')
    ax1.set_ylabel('River Level (feet)')

    if station_id == '04119000':
        plt.title('Grand River at Grand Rapids, MI - 04119000')
    elif station_id == '04119160':
        plt.title('Buck Creek at Wilson Avenue at Grandville, MI - 04119160')
    elif station_id == '04119070':
        plt.title('Grand River at State Hwy M-11 at Grandville, MI - 04119070')
        plt.axhline(y=Wilson_Ave_Flood_Level, color='r', linestyle='-')
        fig.legend(['River Level', 'Estimated Bike Trail Flood Level'])

    ax1.tick_params(rotation=45)
    ax1.set_xticks(ax1.get_xticks()[::4])  # only display one x label per day
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # execute PyQt5 widget
    ex = MyApp()
    sys.exit(app.exec_())