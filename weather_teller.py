import config
import parsing
import translation

import requests
import json
import urllib

from requests import get, post

BAD_QUERY = (-1, -1, -1)

conditions = {
  "clear": "ясно",
  "mostly-clear": "малооблачно",
  "partly-cloudy": "малооблачно",
  "overcast": "пасмурно",
  "partly-cloudy-and-light-rain": "небольшой дождь",
  "partly-cloudy-and-rain": "дождь",
  "overcast-and-rain": "сильный дождь",
  "overcast-thunderstorms-with-rain": "сильный дождь, гроза",
  "cloudy": "облачно с прояснениями",
  "cloudy-and-light-rain": "небольшой дождь",
  "overcast-and-light-rain": "небольшой дождь",
  "cloudy-and-rain": "дождь",
  "overcast-and-wet-snow": "дождь со снегом",
  "partly-cloudy-and-light-snow": "небольшой снег",
  "partly-cloudy-and-snow": "снег",
  "overcast-and-snow": "снегопад",
  "cloudy-and-light-snow": "небольшой снег",
  "overcast-and-light-snow": "небольшой снег",
  "cloudy-and-snow": "снег",
  "wind-n": "северный",
  "wind-n-short": "С",
  "wind-nw": "северо-западный",
  "wind-nw-short": "СЗ",
  "wind-w": "западный",
  "wind-w-short": "З",
  "wind-sw": "юго-западный",
  "wind-sw-short": "ЮЗ",
  "wind-s": "южный",
  "wind-s-short": "Ю",
  "wind-se": "юго-восточный",
  "wind-se-short": "ЮВ",
  "wind-e": "восточный",
  "wind-e-short": "В",
  "wind-ne": "северо-восточный",
  "wind-ne-short": "СВ",
  "wind-c": "штиль",
  "wind-c-short": "штиль",
  "full-moon": "Полнолуние",
  "decreasing-moon": "Убывающая луна",
  "last-quarter": "Последняя четверть",
  "new-moon": "Новолуние",
  "growing-moon": "Растущая луна",
  "first-quarter": "Первая четверть"
}

conditions_to_search = {
  "clear": "sunny",
  "mostly-clear": "sunny",
  "partly-cloudy": "cloudy",
  "overcast": "cloudy",
  "partly-cloudy-and-light-rain": "cloudy",
  "partly-cloudy-and-rain": "rainy",
  "overcast-and-rain": "thunderstorm",
  "overcast-thunderstorms-with-rain": "thunderstorm",
  "cloudy": "cloudy",
  "cloudy-and-light-rain": "rainy",
  "overcast-and-light-rain": "rainy",
  "cloudy-and-rain": "rainy",
  "overcast-and-wet-snow": "rainy",
  "partly-cloudy-and-light-snow": "snowy",
  "partly-cloudy-and-snow": "snowy",
  "overcast-and-snow": "snowy",
  "cloudy-and-light-snow": "snowy",
  "overcast-and-light-snow": "snowy",
  "cloudy-and-snow": "snowy",
}

def get_regions():
	url = 'https://api.weather.yandex.ru/v1/locations?lang=ru-RU'
	header = {
		'X-Yandex-API-Key': config.WEATHER_API
	}
	req = requests.get(url, headers=header)
	response = json.loads(req.content.decode('utf-8'))
	city_geoid = {}
	for city in response:
		 city_geoid[city['name'].lower()] = city['geoid']

	with open('cities.txt', 'w') as r: 
		json.dump(city_geoid, r)

def parse_forecast(forecast):
	temp = forecast.get('temp', None)
	if temp is None:
		temp = forecast.get('temp_avg')
	temp_feels_like = forecast.get('feels_like')
	condition = forecast.get('condition')
	wind_speed = forecast.get('wind_speed')
	pressure = forecast.get('pressure_mm')
	humidity = forecast.get('humidity')
	message = '''{}.\nСредняя температура: {} С.\nОщутимая температура: {} С.
Влажность воздуха: {}%.\nСредняя скорость ветра: {} м/с.\nДавление: {} мм. рт.ст. 
	'''.format(conditions[condition].title(), temp, temp_feels_like, humidity,
		wind_speed, pressure)

	return conditions_to_search[condition], message


class Forecaster(object):
	regions = json.loads(open('cities.txt', 'r').read())
	message_parser = parsing.Parser()
	translator = translation.Translator()

	def __init__(self):
		super().__init__()
		self.__header = {
			'X-Yandex-API-Key': config.WEATHER_API
		}
		self.__req = 'https://api.weather.yandex.ru/v1/forecast?geoid={}&limit={}?l10n={}'


	def forecast(self, message):
		request = Forecaster.message_parser.parse(message)
		
		if request[0] == -1:
			return BAD_QUERY

		city, shift, period = request
		city_eng = Forecaster.translator.translate_to_en(city)[0].lower()
		
		if city_eng == -1:
			return BAD_QUERY

		forecast_geoid = Forecaster.regions.get(city_eng, None)
		if forecast_geoid is None:
			return BAD_QUERY
		
		request = self.__req.format(forecast_geoid,
									               min(10, max(shift, 2)),
									               'true')
		request = requests.get(request, headers=self.__header)
		response = json.loads(request.content.decode('utf-8'))
		forecast = response['fact']

		if shift > 0:
			forecast = response['forecasts'][min(shift, 10)]
			forecast = forecast['parts'][period]

		img_weather, str_message = parse_forecast(forecast)

		return (img_weather, city_eng, str_message)
