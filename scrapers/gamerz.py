from utils.imports import *
import boto3

vendor = "Gamerz.pk"

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
        "Processor": "processor-2/",
        "GPU": "gpu/",
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

    # urls = get_links("processor-2/")

    # print("URLs fetched: ", urls)
    # print('Total links:', len(urls))

    # scrape_data(urls)
    # insert_into_db(client, DATA, vendor)


def get_links(category):
    link = "https://gamerz.pk/product-category/"+category
    print("Fetching links from: ", link)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}
    page = requests.get(link, headers=headers)

    urls = []
    soup = BeautifulSoup(page.content, "html.parser")
    titles = soup.find_all(
        "h3", class_="heading-title product-name")
    for title in titles:
        product_link = title.find("a").get("href")
        urls.append(product_link)
    return urls


def scrape_data(url_dict):
    for category, urls in url_dict.items():
        for link in urls:
            print("Fetching data from: ", link)
            # Fetch the page content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

            page = requests.get(link, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")

            name = soup.find(
                "h1", class_="product_title entry-title").text.strip()

            try:
                price = soup.find(
                    "p", class_="price").find("span").find("bdi").text

            except:
                print("Price not found")
                continue

            warranty = soup.find("li", text=re.compile(r'Warranty'))
            if warranty == None:
                warranty = soup.find("li", text=re.compile(r'months'))
                if warranty == None:
                    warranty = "Not Available"
                else:
                    warranty = warranty.text
            else:
                warranty = warranty.text

            in_stock = soup.find("span", class_="availability-text").text
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
    price = int(price.split('\u20a8', 1)
                [-1].strip().replace(',', ''))

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
