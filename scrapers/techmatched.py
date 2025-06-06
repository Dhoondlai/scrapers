from utils.imports import *
import boto3
import json

vendor = "TechMatched.com"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

if os.environ.get("IS_LOCAL"):
    print("Using local mongo.")
    client = MongoClient("localhost", 27017)
else:

    # fetch from parameter store
    ssm = boto3.client('ssm', region_name='us-east-1')
    response = ssm.get_parameter(Name='mongo-uri', WithDecryption=True)
    uri = response['Parameter']['Value']
    client = MongoClient(uri)


sys.stdout.reconfigure(encoding='utf-8')

DATA = []


def run(event, context):

    categories = {
        "Processor": "processors/",
        "GPU": "graphics-card-in-pakistan/",
    }

    urls_dict = {}

    for db_category, url_category in categories.items():
        try:
            print("Calling get_links")
            urls = get_links(url_category)
            urls_dict[db_category] = urls
        except Exception as e:
            print(e)
            exit(1)
    print(urls_dict)
    print('Total links:', sum(len(v) for v in urls_dict.values()))

    scrape_data(urls_dict)
    print("Total products scraped: ", len(DATA))
    insert_into_db(client, DATA, vendor)

    # urls = get_links("processors/")

    # print("URLs fetched: ", urls)
    # print('Total links:', len(urls))

    # scrape_data(urls)
    # insert_into_db(client, DATA, vendor)


def get_links(category):
    link = "https://techmatched.pk/product-category/" + category
    print("Scraping link: ", link)

    page = requests.get(link, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    pages = soup.find("ul", class_="page-numbers")
    if pages is None:
        no_of_pages = 1
    else:
        page_numbers = pages.find_all('li')
        no_of_pages = len(list(page_numbers)) - 1
    print("Number of pages : ", no_of_pages)

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
        page = requests.get(link
                            + "/page/" + str(counter)+"/")
    return urls


def scrape_data(url_dict):
    for category, urls in url_dict.items():
        for link in urls:

            print("Fetching data from: ", link)
            page = requests.get(link, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")

            name = soup.find("h1", class_="product_title entry-title").text

            price = soup.find(
                "p", class_="price").text
            if price == "":
                print("Price not found")
                continue

            warranty = soup.find("p", text=re.compile(r'Warranty:'))
            if warranty == None:
                warranty = soup.find("p", text=re.compile(r'Months'))
                if warranty == None:
                    warranty = "Not Available"
                else:
                    warranty = warranty.text
            else:
                warranty = warranty.text

            # print vars
            print("=================Uncleaned data====================\n")
            print_variables(name=name, vendor=vendor, price=price,
                            warranty=warranty, category=category, link=link)
            clean_data(name, vendor, price, warranty, category, link)


def clean_data(name, vendor, price, warranty, category, link):
    # Remove all the useless data as we want everything to be consistent.
    name = name.split("Buy", 1)[-1].strip()
    if category == "Processor":
        if "Box" in name:
            name = name.split("Box")[0].strip()
        elif "Tray" in name:
            name = name.split("Tray")[0].strip()

    # prices
    price = price.split('\u20a8', 1)[-1].strip()
    price = int(price.split('.')[0].replace(',', ''))

    # Cleaned data stored as a dictionary
    cleaned_product = {
        'name': name,
        'vendor': vendor,
        'current_price': price,
        'warranty': warranty,
        'category': category,
        'available': True,
        'link': link,
    }

    print("=================Cleaned data====================\n")
    print_variables(**cleaned_product)

    DATA.append(cleaned_product)
