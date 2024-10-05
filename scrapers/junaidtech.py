from utils.imports import *

vendor = "JunaidTech"

if os.environ.get("IS_LOCAL"):
    client = MongoClient("localhost", 27017)
else:
    # change this to the actual endpoint
    client = MongoClient("localhost", 27017)
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

    # scrape_data(urls_dict)
    # print("Total products scraped: ", len(DATA))
    # insert_into_db(client, DATA, vendor)


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
            page = requests.get(link)
            soup = BeautifulSoup(page.content, "html.parser")
            name = soup.find("h1", class_="product_title entry-title").text
            price = soup.find(
                "p", class_="price").text
            # warranty field starts with "Warranty:"
            warranty = soup.find("p", text=re.compile(r'Warranty:'))
            if warranty == None:
                warranty = soup.find("p", text=re.compile(r'Months'))
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
        'price_low': price,
        'price_high': str(price),
        'warranty': warranty,
        'category': category,
        'available': True,
        'link': link,
    }

    print("=================Cleaned data====================\n")
    print_variables(**cleaned_product)

    DATA.append(cleaned_product)
