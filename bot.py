import telebot
import requests
import pickle
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot("YOUR TOKEN")

def initialization():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    horoscopes = ["Aries ♈", "Taurus ♉", "Gemini ♊", "Cancer ♋", "Leo ♌", "Virgo ♍"]
    horoscopes_1 = ["Libra ♎", "Scorpio ♏", "Sagittarius ♐", "Capricorn ♑", "Aquarius ♒", "Pisces ♓"]
    for horoscope, horoscope_1 in zip(horoscopes, horoscopes_1):
        markup.add(InlineKeyboardButton(text=horoscope, callback_data="horoscope_{}".format(horoscope)),
                    InlineKeyboardButton(text=horoscope_1, callback_data="horoscope_{}".format(horoscope_1)))
    return markup

def settings_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(text="Change Horoscope", callback_data=f"change_horoscope"))
    return markup

def change_horoscope():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    horoscopes = ["Aries ♈", "Taurus ♉", "Gemini ♊", "Cancer ♋", "Leo ♌", "Virgo ♍"]
    horoscopes_1 = ["Libra ♎", "Scorpio ♏", "Sagittarius ♐", "Capricorn ♑", "Aquarius ♒", "Pisces ♓"]
    for horoscope, horoscope_1 in zip(horoscopes, horoscopes_1):
        markup.add(InlineKeyboardButton(text=horoscope, callback_data="change_{}".format(horoscope)),
                    InlineKeyboardButton(text=horoscope_1, callback_data="change_{}".format(horoscope_1)))
    return markup

def horoscope_done_troll(horoscope):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(text="You are a " + horoscope + " now!", callback_data="hehe"))
    return markup


my_dict =  {"Aries":1,
            "Taurus":2,             
            "Gemini":3,
            "Cancer":4,
            "Leo":5,
            "Virgo":6,
            "Libra":7,
            "Scorpio":8,
            "Sagittarius":9,
            "Capricorn":10,
            "Aquarius":11,
            "Pisces":12,
            }

@bot.message_handler(commands=["start"])
def cmd_start(message):
        msg = """Hi! Before we start, I would like you to choose your zodiac sign. Press the below buttons to choose your zodiac sign!\n\nI am a..."""
        bot.send_message(message.chat.id, text = msg, reply_markup=markup.initialization())

def initialization_complete(message, horoscope):
    msg = """Welcome {}. You can /subscribe to our daily horoscope notifications, or /unsubscribe if you do not wish to receive any more notifications.\n\nEven if you unsubscribed, you can still use our commands. Tap /help to see more."""
    bot.edit_message_text(chat_id = message.chat.id,
                            message_id = message.message_id,
                            text = msg.format(horoscope))


@bot.message_handler(commands=["help"])
def cmd_help(message):
    msg = """*Available commands*\n\n/today - View today's horoscope.\n/tomorrow - Not available yet\n/settings - to change your horoscope\n/subscribe - to subcribe to daily notifications\n/unsubscribe - to unsubscribe to daily notifications\n\n/surprise - !!!"""
    bot.send_message(message.chat.id, parse_mode="Markdown", text=msg)

@bot.message_handler(commands=["today"])
def web_scrap_today(message):
    try:
        sign = my_dict[horoscope]
        url = "https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-today.aspx?sign={}".format(sign)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        data = soup.find_all("main", class_="main-horoscope")[0]
        date = data.p.strong.text
        todays_horoscope = data.p.strong.next_sibling.replace("-", "")
        bot.send_message(message.chat.id, text = date + " - " + horoscope +"\n\n" + todays_horoscope)
    except:
        bot.send_message(message.chat.id, text = "Unable to get today's zodiac sign... 😭😭")

@bot.message_handler(commands=["tomorrow"])
def web_scrap_tomorrow(message):
    bot.send_message(message.chat.id, text="This command is not available yet.")

@bot.message_handler(commands=["settings"])
def settings(message):
    bot.send_message(message.chat.id, text="What would you like to do?", reply_markup=markup.settings_menu())

def settings_change_horoscope(message):
	bot.edit_message_text(chat_id=message.chat.id,
                        message_id=message.message_id,
                        text="Choose your horoscope again",
                        reply_markup=markup.change_horoscope())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("horoscope_"):
        horoscope = call.data.split("_")[1]
        horoscope = horoscope.split(" ")[0]
        bot.answer_callback_query(call.id, text="Ey wassup " + horoscope + "!", show_alert=True)
        dbworker.initialize_user(call.message.chat.id, horoscope)
        initialization_complete(call.message, horoscope)
    elif call.data == "change_horoscope":
        bot.answer_callback_query(call.id)
        settings_change_horoscope(call.message)
    elif call.data.startswith("change_"):
        bot.answer_callback_query(call.id)
        horoscope = call.data.split("_")[1]
        horoscope = horoscope.split(" ")[0]
        dbworker.change_db_horoscope(call.message.chat.id, horoscope)
        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text="Change Completed! Tap /today to view your horoscope 😄",
                            reply_markup=markup.horoscope_done_troll(horoscope))
    elif call.data == "hehe":
        bot.answer_callback_query(call.id, text="hehe")

        

if __name__ == '__main__':
    bot.polling(none_stop=True)
