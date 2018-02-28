import config

import http.client
import json
import urllib.parse


class ImageFinder(object):
    def __init__(self):
        self.__city = None
        self.__weather = None
        self.__query = None
        self.__params = None
        self.__headers = {
            'Ocp-Apim-Subscription-Key': config.SEARCH_API
        }

    def set_params(self, weather=None, city=None):
        if weather is None:
            weather = 'sunny'
        if city is None:
            city = 'kek'

        self.__weather = weather
        self.__city = city
        self.__query = "{} weather in {}".format(self.__weather,
                                                 self.__city)
        self.__params = urllib.parse.urlencode({
            'q': self.__query,
            'count': 10,
            'mkt': 'en-EN',
            'safeSearch': 'Moderate'
        })

    def search(self):
        try:
            img_url = self.__search()
        except IndexError:
            self.set_params(self.__weather, '')
            img_url = self.__search()
        return img_url

    def __search(self):
        conn = http.client.HTTPSConnection('api.cognitive.microsoft.com')
        conn.request("GET", "/bing/v7.0/images/search?%s" % self.__params,
                     self.__query.encode('utf-8'), self.__headers)
        response = conn.getresponse()
        string = response.read().decode('utf-8')
        json_obj = json.loads(string)
        img_url = json_obj['value'][0]['contentUrl']
        img_urls = json_obj['value']
        conn.close()
        return img_urls
