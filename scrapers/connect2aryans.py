from utils.imports import *
import boto3

vendor = "Connect2Aryans.com"

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
    urls = get_links("processors")

    print("URLs fetched: ", urls)
    print('Total links:', len(urls))

    scrape_data(urls)
    insert_into_db(client, DATA, vendor)


def get_links(category):
    link1 = "https://connect2aryans.com/ryzen-processors"
    link2 = "https://connect2aryans.com/intel-processors-price-in-pakistan"
    urls = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

    get_each(link1)
    get_each(link2)

    def get_each(link):
        print("Fetching links from: ", link)
        page = requests.get(link, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        links = soup.find_all(
            "a", class_="block-product-list__link")
        for link in links:
            urls.append(link.get("href"))

    return urls


def scrape_data(urls):
    category = "Processor"
    for link in urls:
        link = "https://connect2aryans.com" + link
        print("Fetching data from: ", link)
        # Fetch the page content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

        page = requests.get(link, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        name = soup.find(
            "h1", class_="block-product__title").text.strip()

        try:
            price = soup.find(
                "span", class_="block-product__price body-large").text.strip()
        except:
            print("Price not found")
            continue

        warranty = "Not Available"

        in_stock = True

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
        'price_low': price,
        'price_high': str(price),
        'warranty': warranty,
        'category': category,
        'available': available,
        'link': link,
    }

    print("=================Cleaned data====================")
    print_variables(**cleaned_product)

    DATA.append(cleaned_product)
