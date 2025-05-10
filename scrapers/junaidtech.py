from utils.imports import *
import boto3

vendor = "JunaidTech.pk"

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
    # categories mapped as per in the link
    # only setting up data with processors now.
    print("Starting" + vendor + " scraper")

    categories = {
        "Processor": "processors-cpu",
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


def get_links(category):
    link = "https://www.junaidtech.pk/"+category
    print("Fetching links from: ", link)
    page = requests.get(link)

    urls = []
    counter = 1
    while True:
        soup = BeautifulSoup(page.content, "html.parser")
        titles = soup.find_all("h4", {"name": "list-productname"})
        if titles == []:
            break
        for title in titles:
            product_link = title.find("a").get("href")
            urls.append(product_link)
        counter += 1
        new_page_link = link + "?sort=1&page=" + str(counter)
        print("\nCalling new page: ", new_page_link)
        page = requests.get(new_page_link)

    return urls


def scrape_data(url_dict):
    for category, urls in url_dict.items():
        for link in urls:
            link = "https://www.junaidtech.pk" + link
            print("Fetching data from: ", link)
            # Fetch the page content
            page = requests.get(link)
            soup = BeautifulSoup(page.content, "html.parser")

            name = soup.find("h1", class_="product-title").text

            price = soup.find(
                "span", class_="price-sales").text

            warranty = soup.find("span", id="spnWarranty")
            if warranty == None:
                warranty = "Not Available"
            else:
                warranty = warranty.text

            in_stock = soup.find("span", id="spnStockStatus").text
            if in_stock == "In Stock":
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
    price = int(price.split('Rs.', 1)[-1].strip().replace(',', ''))

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
