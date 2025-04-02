# River Tracking Tools Python Codebase 

## **Tools:**
### **River Level GUI**: 
**Description**: User selects the USGS station by river location and city, and chooses 5 to 21 days of data. The data is downloaded, sampled, and displayed in appropriate increments.

## Prerequisites

- **Python 3.8+**
- Required packages:
  - `PyQt5`: GUI framework
  - `requests`: HTTP requests for data download
  - `pandas`: Data manipulation
  - `matplotlib`: Data visualization

Install dependencies via pip:
```bash
pip install PyQt5 requests pandas matplotlib
```

## Project Structure

- `River Level Tracker.py`: Main application file containing the GUI, data download, and visualization logic.
- `river_level_data.rdb`: Output file where downloaded river data is saved (generated at runtime).

## How to Run

1. **Clone or Download**: Ensure `River Level Tracker.py` is in your working directory.
2. **Install Dependencies**: Run the pip command above to install required packages.
3. **Execute the Program**:
   ```bash
   python "River Level Tracker.py"
   ```
