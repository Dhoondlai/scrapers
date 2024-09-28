from utils.imports import *

vendor = "TechMatched"

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
    # Will slowly start adding others as data makes more sense.

    categories = {
        "Processor": "processors",
        # "Motherboard": "motherboards",
        # "Thermal Paste": "thermal-paste",
        # "CPU Cooler": "cpu-coolers",
        # "RAM": "rams",
        # "Casing": "computer-case",
        # "Fan": "fans-kits",
        # "Power Supply": "buy-power-supply-in-pakistan",
        # "Graphics Card": "graphics-card-in-pakistan",
        # "Gaming Monitor": "gaming-monitors",
        # "Gaming Chair": "gaming-chairs",
        # "Mouse": "gaming-mouse",
        # "Keyboard": "gaming-keyboards",
        # "Mousepad": "xxl-mousepad",
        # "Headphone": "headphones",
        # "Controller": "pc-controllers",
        # "Cable": "pc-cables",
        # "Webcam": "webcam",
        # "SSD": ["find-ssd-prices-in-pakistan", "nvme-m-2-ssd"],
        # "Hard Drive": "hard-drive"
    }

    # will store all the urls associated with their category.
    ###################################################### Comment this section if you want to test with only one link######################################################
    urls_dict = {}
    for db_category, url_category in categories.items():
        try:
            if db_category == "SSD":
                for category in url_category:
                    urls = get_links(category)
                    urls_dict[category] = urls
            else:
                urls = get_links(url_category)
                urls_dict[db_category] = urls
        except Exception as e:
            print(e)
            exit(1)
    print(urls_dict)
    ###################################################### Comment this section if you want to test with only one link######################################################

    ###################################### Uncomment this section if you want to test with only one link######################################################
    # urls_dict = {'Processor': [
    #     'https://techmatched.pk/product/buy-amd-ryzen-7-7950x-3d-desktop-processor/']}
    ###################################### Uncomment this section if you want to test with only one link################################################

    scrape_data(urls_dict)
    insert_into_db(client, DATA)


def get_links(category):
    link = "https://techmatched.pk/product-category/" + category
    if category in ["gaming-mouse", "gaming-keyboards", "xxl-mousepad", "headphones", "pc-controllers", "pc-cables", "webcam"]:
        link = "https://techmatched.pk/product-category/gaming-peripherals/" + category
    elif category in ["find-ssd-prices-in-pakistan", "nvme-m-2-ssd", "hard-drive"]:
        link = "https://techmatched.pk/product-category/storage/" + category
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    # get number of pages
    pages = soup.find("ul", class_="page-numbers")
    if pages is None:
        no_of_pages = 1
    else:
        page_numbers = pages.find_all('li')
        # -1 is for the "next" button
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
        'price_low': str(price),
        'price_high': str(price),
        'warranty': warranty,
        'category': category,
        'link': link
    }

    print("=================Cleaned data====================\n")
    print_variables(**cleaned_product)

    DATA.append(cleaned_product)
