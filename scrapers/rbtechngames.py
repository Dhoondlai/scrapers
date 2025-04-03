from utils.imports import *
import boto3

vendor = "RBTechNGames"

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
    urls = get_links("processors/")

    print("URLs fetched: ", urls)
    print('Total links:', len(urls))

    scrape_data(urls)
    insert_into_db(client, DATA, vendor)


def get_links(category):
    link = "https://rbtechngames.com/product-category/computers/"+category
    print("Fetching links from: ", link)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}
    page = requests.get(link, headers=headers)

    urls = []
    counter = 1
    while True:
        soup = BeautifulSoup(page.content, "html.parser")
        titles = soup.find_all(
            "p", class_="name product-title woocommerce-loop-product__title")
        if titles == []:
            break
        for title in titles:
            product_link = title.find("a").get("href")
            urls.append(product_link)
        counter += 1
        new_page_link = link + "page/" + str(counter) + "/"
        print("\nCalling new page: ", new_page_link)
        page = requests.get(new_page_link)

    return urls


def scrape_data(urls):
    category = "Processor"
    for link in urls:
        print("Fetching data from: ", link)
        # Fetch the page content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

        page = requests.get(link, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        name = soup.find(
            "h1", class_="product-title product_title entry-title").text.strip()

        try:
            price = soup.find(
                "div", class_="price-wrapper").find("ins").find("bdi").text
        except:
            price = soup.find(
                "div", class_="price-wrapper").find("bdi").text

        warranty = "Not Available"

        in_stock = soup.find("p", class_="stock in-stock").text
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
    price = int(price.split('\u20a8', 1)[-1].strip().replace(',', ''))

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
