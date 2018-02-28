import telebot

import config
import poems

import image_search
import messages
import translation
import weather_teller


bot = telebot.TeleBot(config.TELEGRAM_API)


@bot.message_handler(commands=['start'])
def start_handler(message):
	bot.reply_to(message, messages.HELLO)

@bot.message_handler(commands=['help'])
def help_handler(message):
	bot.reply_to(message, messages.HELP)

@bot.message_handler(commands=['forecast', 'predict'])
@bot.message_handler(content_types=["text"])
def forecast_handler(message):
	forecaster = weather_teller.Forecaster()
	weather_condition, city, ans_message = forecaster.forecast(message.text)
	
	if weather_condition == -1:
		bot.reply_to(message, messages.INVALID_INPUT)
		return

	bot.reply_to(message, ans_message)

	image_finder = image_search.ImageFinder()
	image_finder.set_params(weather_condition, city)
	picture_url = image_finder.search()

	picture_index = 0
	picture_send = False
	while not picture_send and picture_index < len(picture_url):
		try:
			bot.send_photo(chat_id=message.chat.id, photo=picture_url[picture_index]['contentUrl'])
			picture_send = True
		except Exception:
			picture_index += 1

	if picture_send:
		bot.send_message(message.chat.id, poems.poems[weather_condition])
	else:
		bot.reply_to(message, messages.IMAGE_PROBLEMS)


if __name__ == "__main__":
	bot.polling(none_stop=True)
