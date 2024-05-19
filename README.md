# 🏰 Disney Holiday Scraper

This is a personal project to scrape flight, hotel, and ticket prices from the UK Disney holiday booking site. It is intended for personal educational use only and no support, other than what is listed here, is intended.

<br></br>
## 📋 Table of Contents

- [Description](#-description)
- [Requirements](#-requirements)
- [Setup](#-setup)
- [Usage](#-usage)
- [Configuration](#-configuration)


<br></br>
## ✨ Description
 
- **Multithreading**: Speeds up data scraping by running multiple threads
- **Customisable Search**: Modify the search criteria through a configuration file
- **Export to CSV**: Collects data and exports it into a CSV file for easy analysis
- **Retry Mechanism**: Handles failures with retry and  backoff mechanisms

<br></br>
## 💻 Requirements

- Python 3.7 or later
- `requests` library
- `beautifulsoup4` library
- `pandas` library
- `tqdm` library
- `concurrent.futures` module

<br></br>
## ⚙️ Setup

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/neoreuvenla/disney-holiday-scraper.git
    cd disney-holiday-scraper
    ```

2. **Setup Virtual Environment and Install Dependencies**:

    ```bash
    ./setup.sh
    ```

<br></br>
## 🚀 Usage

1. **Activate the Virtual Environment**:

    ```bash
    source venv/bin/activate
    ```

2. **Run the Main Script**:

    ```bash
    ./scraper.sh
    ```

    Follow the on-screen menu to choose the type of data you want to scrape. Multiple options can be queued:
    - **1**: Disney flight, hotel, and ticket scraping
    - **2**: Disney hotel scraping
    - **3**: Disney ticket scraping
    - **4**: Edit config in terminal
    - **5**: Exit

<br></br>
## 🛠️ Configuration

Customize your search parameters by editing the `config.py` file. For example, changing the range of days, months, and nights to be checked:

- **Days**: `days = list(map(str, range(1, 31)))`
- **Months**: `months = [f'{month}^{year}' for month in range(1, 13) for year in [2025]]`
- **Nights**: `nights = list(map(str, range(7, 15)))`