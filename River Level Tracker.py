import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
import pandas as pd
import matplotlib.pyplot as plt

Wilson_Ave_Flood_Level = 8.25  # estimated flood level in feet

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 360, 200)
        self.setWindowTitle('River Data Downloader')

        self.site_id = ''

        self.combo = QComboBox(self)
        self.combo.addItem('Grand River - Wilson Ave Bridge')
        self.combo.addItem('Grand River - Downtown GR')
        self.combo.addItem('Buck Creek at Wilson Ave')
        self.combo.move(50, 50)

        self.combo.currentTextChanged.connect(self.updateSiteId)

        self.button = QPushButton('Download and Display Data', self)
        self.button.move(75, 100)
        self.button.clicked.connect(self.downloadAndDisplayData)

        self.show()

    def updateSiteId(self, text):  # set river station ID based on dropdown menu
        if text == 'Grand River - Wilson Ave Bridge':
            self.site_id = '04119070'
        elif text == 'Grand River - Downtown GR':
            self.site_id = '04119000'
        elif text == 'Buck Creek at Wilson Ave':
            self.site_id = '04119160'

    def downloadAndDisplayData(self):  # button to execute functions
        download_river_data(self.site_id)
        display_river_data(self.site_id)


'''
Function: download_river_data
Inputs: river station ID
Outputs: None
Description: Downloads 30 days of data for a selected river station from the USGS API. The data is saved locally into 
a file named river_level_data.rdb
'''
def download_river_data(station_id):

    # Get current date and time
    current_datetime = datetime.now()

    # Calculate date 30 days ago
    start_datetime = current_datetime - timedelta(days=30)

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
Description: Loads and displays the river data in 6hr increments for a selected river station
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

    fig, ax1 = plt.subplots(figsize=(12, 8))  # create a subplot and add labels
    # Plot river level data
    ax1.plot(df_6h['datetime'], df_6h['level'])
    ax1.set_xlabel('Date (6 hr Increments)')
    ax1.set_ylabel('River Level (feet)')

    if station_id == '04119000':
        plt.title('River Level Over Past 30 Days \n Grand River at Grand Rapids, MI - 04119000')
    elif station_id == '04119160':
        plt.title('Buck Creek Level Over Past 30 Days \n Buck Creek at Wilson Avenue at Grandville, MI - 04119160')
    elif station_id == '04119070':
        plt.title('River Level Over Past 30 Days \n Grand River at State Hwy M-11 at Grandville, MI - 04119070')
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