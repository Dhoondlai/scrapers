# BORKED.

from utils.imports import *
import boto3

vendor = "BuyersPk.com"

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
    print("Starting" + vendor + " scraper")

    categories = {
        "Processor": "intel-and-amd-processor-cpu-price-in-pakistan",
        "GPU": "graphic-card-pakistan",
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

    # urls = get_links("intel-and-amd-processor-cpu-price-in-pakistan")

    # print("URLs fetched: ", urls)
    # print('Total links:', len(urls))

    # scrape_data(urls)
    # insert_into_db(client, DATA, vendor)


def get_links(category):
    link = "https://www.buyerspk.com/collections/"+category
    print("Fetching links from: ", link)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    page = requests.get(link, headers=headers)

    urls = []
    counter = 1
    while True:
        soup = BeautifulSoup(page.content, "html.parser")
        print(soup)
        titles = soup.find_all(
            "h3", class_="product-card_title")
        print("Found titles: ", len(titles))
        if titles == []:
            break
        for title in titles:
            product_link = title.find("a").get("href")
            urls.append(product_link)
        counter += 1
        new_page_link = link + "?page=" + str(counter)
        print("\nCalling new page: ", new_page_link)
        page = requests.get(new_page_link, headers=headers)

    return urls


def scrape_data(url_dict):
    for category, urls in url_dict.items():
        for link in urls:
            link = "https://www.buyerspk.com/" + link
            print("Fetching data from: ", link)
            # Fetch the page content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

            page = requests.get(link, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")

            name = soup.find(
                "h1", class_="page-heading").text.strip()

            price = soup.find(
                "span", class_="price").text.strip()

            warranty = "Not Available"

            in_stock = soup.find("span", class_="stock").text
            if "in stock" in in_stock.lower():
                in_stock = True
            else:
                in_stock = False

            # print vars
            print("=================Uncleaned data====================")
            print_variables(name=name, vendor=vendor, price=price,
                            warranty=warranty, category=category, link=link, in_stock=in_stock)

            clean_data(name, vendor, price, warranty, category, link, in_stock)


def clean_data(name, vendor, price, warranty, category, link, in_stock):

    available = True
    if not in_stock:
        available = False

    # remove any "-" to handle consistency in intel processors
    name = name.replace("-", " ")

    # prices
    price = int(price.split('Rs.', 1)
                [-1].strip().replace(',', '').split('.')[0])

    cleaned_product = {
        'name': name,
        'vendor': vendor,
        'current_price': price,
        'warranty': warranty,
        'category': category,
        'available': available,
        'link': link,
    }

    print("=================Cleaned data====================")
    print_variables(**cleaned_product)

    DATA.append(cleaned_product)
