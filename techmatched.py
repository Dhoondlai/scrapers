from bs4 import BeautifulSoup
import requests
import re


def run(event, context):
    # categories mapped as per in the url
    categories = {
        "Processor": "processors",
        "Motherboard": "motherboards",
        "Thermal Paste": "thermal-paste",
        "CPU Cooler": "cpu-coolers",
        "RAM": "rams",
        "Casing": "computer-case",
        "Fan": "fans-kits",
        "Power Supply": "buy-power-supply-in-pakistan",
        "Graphics Card": "graphics-card-in-pakistan",
        "Gaming Monitor": "gaming-monitors",
        "Gaming Chair": "gaming-chairs",
        "Mouse": "gaming-mouse",
        "Keyboard": "gaming-keyboards",
        "Mousepad": "xxl-mousepad",
        "Headphone": "headphones",
        "Controller": "pc-controllers",
        "Cable": "pc-cables",
        "Webcam": "webcam",
        "SSD": ["find-ssd-prices-in-pakistan", "nvme-m-2-ssd"],
        "Hard Drive": "hard-drive"
    }
    urls_dict = {}
    for db_category, url_category in categories.items():
        if db_category == "SSD":
            for category in url_category:
                urls = get_links(category)
                try:
                    urls_dict[category] = urls
                except Exception as e:
                    continue
            continue
        urls = get_links(url_category)
        try:
            urls_dict[category] = urls
        except Exception as e:
            continue
        print(urls_dict)


def get_links(category):
    url = "https://techmatched.pk/product-category/" + category
    if category in ["gaming-mouse", "gaming-keyboards", "xxl-mousepad", "headphones", "pc-controllers", "pc-cables", "webcam"]:
        url = "https://techmatched.pk/product-category/gaming-peripherals/" + category
    elif category in ["find-ssd-prices-in-pakistan", "nvme-m-2-ssd", "hard-drive"]:
        url = "https://techmatched.pk/product-category/storage/" + category
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    # get number of pages
    pages = soup.find("ul", class_="page-numbers")
    if pages is None:
        no_of_pages = 1
    else:
        page_numbers = pages.find_all('li')
        print(len(list(page_numbers)))
        # -1 is for the "next" button
        no_of_pages = len(list(page_numbers)) - 1

    urls = []
    counter = 1
    while True:
        soup = BeautifulSoup(page.content, "html.parser")
        titles = soup.find_all("a", text=re.compile(r'(?i)buy'))
        if titles == []:
            break
        for title in titles:
            link = title.get("href")
            urls.append(link)
        counter += 1
        if counter > no_of_pages:
            break
        page = requests.get(url
                            + "/page/" + str(counter)+"/")
    return urls
