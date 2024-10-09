# Human Rights Watch News Scraper

This project is a web scraper built using Python to collect articles from the Human Rights Watch (HRW) website. The scraper navigates through multiple pages, extracts the news articles, and saves the content to CSV files and HTML files locally. This project uses the `selenium_driverless` library, making it capable of browsing the website and interacting with elements like a human would.

## Requirements

Before running this project, ensure you have the following installed:

- [Python 3.8+](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/) (this scraper uses Google Chrome to browse the website)
- [Poetry](https://python-poetry.org/docs/#installation) (a dependency manager for Python)

## Installation

1. **Install Python**  
    Download and install Python from the [official website](https://www.python.org/downloads/).

2. **Install Google Chrome**  
    Download and install Google Chrome from the [official website](https://www.google.com/chrome/).

3. **Install Poetry**  
    Poetry is a dependency management tool for Python. You can install Poetry by following the instructions [here](https://python-poetry.org/docs/#installation).

    For Windows:
    ```bash
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    ```

    For Linux/macOS:
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

4. **Clone the Repository**
    Download the project files by cloning the repository to your local machine:
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

5. **Install Dependencies**
    Use Poetry to install the project dependencies:
    ```bash
    poetry install
    ```

## Running the Scraper

1. **Activate the Poetry Environment**
    Activate the virtual environment created by Poetry:
    ```bash
    poetry shell
    ```

2. **Run the Scraper**
    After activating the shell, you can run the scraper with the following command:
    ```bash
    python main.py
    ```

## Project Structure

- **hrw_news.csv**: This file will be created after the scraper runs and will contain the extracted articles in CSV format.
- **html_files/**: This folder will store the HTML versions of the articles for future reference.
- **hrw_news_errors.csv**: This file will log any errors that occurred during the scraping process.

## How the Scraper Works

1. The scraper navigates to the HRW news page and extracts the main articles on the page.
2. It saves each article's title, date, content, topics, and related countries to a CSV file.
3. The content is also saved as separate HTML files in the html_files folder.
4. The scraper continues navigating through pages until it reaches articles that are older than 2023.

## Additional Information

This project uses libraries like selenium_driverless, BeautifulSoup, and asyncio to handle browser automation, HTML parsing, and asynchronous operations. If you encounter any issues during the installation or execution, feel free to open an issue or ask for help!

## Troubleshooting

- Google Chrome Version Mismatch: Ensure that the selenium_driverless library is compatible with the version of Google Chrome installed on your system.
- Permission Errors: If you encounter permission issues while creating files, try running the script with elevated privileges.
