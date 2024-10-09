from utils import start_driver, wait_for_selector, save_success_csv
from tenacity import retry, stop_after_attempt, wait_fixed
from selenium_driverless.types.by import By
from rich.console import Console
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import asyncio
import csv
import sys
import re
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir_abspath = os.path.abspath(current_dir)
csv.field_size_limit(sys.maxsize)

console = Console()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def sanitize_filename(filename):
    valid_chars = r"[^a-zA-Z0-9\s\-_]"
    sanitized = re.sub(valid_chars, "", filename)
    sanitized = re.sub(r"\s+", " ", sanitized.strip())
    sanitized = sanitized.strip("_")
    sanitized = sanitized.strip().rstrip(".")
    return sanitized


@retry(stop=stop_after_attempt(10), wait=wait_fixed(5))
async def parse_articles(driver, articles):
    saved_urls = set()
    csv_path = f"{current_dir_abspath}/hrw_news.csv"

    if os.path.exists(csv_path):
        with open(csv_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            saved_urls = set(row["URL"] for row in reader)

    for article in articles:
        try:
            url = article.select_one("a").get("href")

            if f"https://www.hrw.org{url}" in saved_urls:
                console.print(f"[bold aquamarine3]Skipping already saved article: {url}[/bold aquamarine3]")
                continue

            if "/news/" not in url or "/top-human-rights-" in url:
                console.print(f"[bold bright_cyan]Skipping non-news article: {url}[/bold bright_cyan]")
                continue

            logging.info("Moving to specific article page")
            article_element = await driver.find_element(By.CSS_SELECTOR, f"a[href='{article.select_one('a').get('href')}']")
            await driver.execute_script("arguments[0].click();", article_element)
        except Exception as e:
            console.print("[bold red]Error while moving to specific article page[/bold red]")
            await driver.refresh()
            await driver.sleep(1)
            raise e

        try:
            logging.info("Waiting article page loads")
            await wait_for_selector(driver, By.CSS_SELECTOR, "div[class*='article-body']", visible=True, check_interval=0.1)
            await driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await driver.sleep(0.5)

            url = await driver.current_url

            if "/news/" not in url:
                console.print(f"[bold bright_cyan]Skipping non-news article: {url}[/bold bright_cyan]")
                logging.info("Back to news page")
                await driver.back()
                logging.info("Waiting news page loads")
                await wait_for_selector(driver, By.CSS_SELECTOR, "article div[class*='content']", visible=True, check_interval=0.1)
                await driver.sleep(0.5)
                continue

            # Extract the article content
            logging.info("Extracting article content")
            content = await driver.page_source
            soup = BeautifulSoup(content, "html.parser")

            date_match = re.search(r"/(\d{4}/\d{2}/\d{2})/", url)
            date_str = date_match.group(1)
            date_obj = datetime.strptime(date_str, "%Y/%m/%d")
            formatted_date = date_obj.strftime("%m/%d/%Y")

            topics = soup.find("div", string="Topic").find_next_sibling("ul").find_all("li") if soup.find("div", string="Topic") else ""
            topics = ", ".join([topic.text for topic in topics]) if topics else ""

            countries = (
                soup.find("div", string="Region / Country").find_next_sibling("ul").find_all("li")
                if soup.find("div", string="Region / Country")
                else ""
            )
            countries = ", ".join([country.text for country in countries]) if countries else ""

            title = soup.select_one("h1[class*='title']").text

            if not title:
                console.print("[bold red]No title found. Retrying...[/bold red]")
                raise Exception("No title found")

            html_name = soup.select_one("h1[class*='title']").text.replace("/", "-").replace(":", "-")
            html_name = sanitize_filename(html_name)

            article_body = soup.select_one("div[class*='article-body']")

            if article_body:
                page_content = article_body.text.replace("\n", " ").replace("Click to expand Image", "").strip()
            else:
                page_content = soup.select("div[class*='container']")
                page_content = " ".join([p.text.replace("\n", " ").replace("Click to expand Image", "").strip() for p in page_content])

            article_content = {
                "URL": url,
                "html_name": html_name,
                "Title": title,
                "Subtitle": soup.select_one("p[class*='subtitle']").text if soup.select_one("p[class*='subtitle']") else soup.select_one("h2").text,
                "Date": formatted_date,
                "Content": page_content,
                "Country": countries,
                "Topics": topics,
            }

            logging.info("Saving article content in csv")
            save_success_csv(
                article_content,
                f"{current_dir_abspath}/hrw_news.csv",
            )

            logging.info("Saving article content in html")
            with open(f"{current_dir_abspath}/html_files/{html_name}.html", "w", encoding="utf-8") as file:
                file.write(content)

            console.print(f"[bold green]Article saved! \nTitle: {title} \nCountry: {countries} \nTopics: {topics} \nUrl: {url}[/bold green]")
            logging.info("Back to news page")
            await driver.back()

            logging.info("Waiting news page loads")
            await wait_for_selector(driver, By.CSS_SELECTOR, "article div[class*='content']", visible=True, check_interval=0.1)
            await driver.sleep(0.5)
        except Exception as e:
            await driver.back()
            await wait_for_selector(driver, By.CSS_SELECTOR, "article div[class*='content']", visible=True, check_interval=0.1)
            await driver.sleep(0.5)
            console.print(f"[bold red]Error parsing article: {url}[/bold red]")
            raise e


@retry(stop=stop_after_attempt(10), wait=wait_fixed(5))
async def parse_page(driver):
    logging.info("Waiting page loads")
    await wait_for_selector(driver, By.CSS_SELECTOR, "article div[class*='content']", visible=True)

    logging.info("Parsing the page content")
    soup = BeautifulSoup(await driver.page_source, "html.parser")
    articles = soup.select("article div[class*='content']")

    if not articles:
        console.print("\n[bold red]No articles found. Retrying...[/bold red]")
        raise Exception("No articles found")

    logging.info(f"Found {len(articles)} articles")

    await parse_articles(driver, articles)

    next_button = await wait_for_selector(driver, By.CSS_SELECTOR, "a[title*='next page'][rel='next']", visible=True, timeout=30)

    if not next_button:
        return True

    await driver.execute_script("arguments[0].click();", next_button)
    logging.info("Moving to the next page")
    await driver.sleep(1)


async def main():
    driver = await start_driver()
    await driver.get("https://www.hrw.org/news?page=2671", wait_load=True)
    keep_going = True

    while keep_going:
        stop = await parse_page(driver)
        if stop:
            keep_going = False

    console.print("[bold green]All articles have been saved.[/bold green]")
    await driver.quit()


asyncio.run(main())
