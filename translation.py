import config

import requests
import json
import urllib

from requests import get, post


class Translator(object):
	
	def __init__(self):
		super().__init__()
		self.__request = "https://translate.yandex.net/api/v1.5/tr.json/translate?key={}&{}&lang={}"

	
	def translate_to_en(self, message):
		request = self.__request.format(config.TRANSLATION_API,
										urllib.parse.urlencode({'text': message}),
										'ru-en')
		req = requests.get(request)
		response = json.loads(req.content.decode('utf-8'))
		if response['code'] == 200:
			return response['text']
		else:
			return -1
