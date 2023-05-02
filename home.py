import os
import telebot
import requests
from pprint import pprint
from bs4 import BeautifulSoup
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

url = ""
# the below handles /start and /hello  commands
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "This bot will look at the prices on Ebay")

@bot.message_handler(commands=['product'])
def item_asker(message):
    product = "Which product are you searching for ?"
    sent_msg = bot.send_message(message.chat.id, product, parse_mode="Markdown")
    # send the product to the get_prices function
    bot.register_next_step_handler(sent_msg, get_data)

def get_data(item):
    # check if how many words item has
    item_text = item.text
    item_word_list = item_text.split()
    item_for_url = ""
    if len(item_word_list) > 1:
        for word in item_word_list:
            if item_word_list.index(word) == 0:
                item_for_url = word
            # if the item_text contains >1 word use '+'
            else:
                item_for_url += '+' + word
    else:
        item_for_url = item_text
    

    url = "https://www.ebay.com.sg/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=" + item_for_url + "&_sacat=0"
    # url = "https://www.ebay.com.sg/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=laptop&_sacat=0"
    # define headers
    headers = {'User-Agent':'Generic user agent'}
    # get the page
    page = requests.get(url, headers=headers) 
    soup = BeautifulSoup(page.text,'html.parser')
    # parse the data
    results = soup.find_all('div', {'s-item__info clearfix'}) #how to know which element to choose? Choose the common one across all listings that is one level above the details
    list_of_products = []
    for listing in results:
        if (listing.find('div', {'class': 's-item__title'}).text == "Shop on eBay"):
            continue
        # below will take some time
        products = {
            'title': listing.find('div', {'class': 's-item__title'}).text,
            'price': listing.find('span', {'class': 's-item__price'}).text.replace(',','').strip() ,
            'link': listing.find('a', {'class', 's-item__link'})['href']
        }
        list_of_products.append(products)
        # format the data for the bot
    for product in list_of_products:
        print(list_of_products.index(product))
        if list_of_products.index(product) < 5:
            bot.send_message(item.chat.id, products['title'])
            bot.send_message(item.chat.id, products['price'])
            bot.send_message(item.chat.id, products['link'])
# below line should automatically run when the item is entered
bot.infinity_polling()
