from datetime import date

class Parser(object):
	weekdays = { 'понедельник' : 0, 'вторник' : 1, 'среду' : 2,
		'четверг' : 3, 'пятницу' : 4, 'субботу' : 5, 'воскресенье' : 6
	}

	daytimes = { 'утром': 'morning', 'днем': 'day', 'вечером': 'evening'}

	def parse(self, telegram_message): 
		text = telegram_message.split()
		if '/' in text[0]:
			text = text[1:]
	
		if len(text) == 1:
			return (text[0], 0, 1)

		elif len(text) == 2:
			if text[1] == 'завтра':
				 return (text[0], 1, 'day')

			elif text[1] == 'сегодня':
				return (text[0], 0, 'day')

			elif text[1] in Parser.daytimes.keys():
				try:
					return (text[0], 0, Parser.daytimes[text[1]])
				except Exception:
					return (-1, 'Неподдерживаемый формат запроса')

			else:
				return (-1, 'Неподдерживаемый формат запроса')

		elif len(text) == 3:
			city = text[0]

			if text[1] in ['в', 'во']:
				week_day = None

				try:
					week_day = Parser.weekdays[text[2]]
				except Exception:
					return (-1, 'Неподдерживаемый формат запроса')

				today = date.today().weekday()

				shift = (week_day - today + (7 if (week_day - today <= 0) else 0)) % 7
				return (city, shift, 'day')

			elif text[1] == 'завтра':
				try:
					return (city, 1, Parser.daytimes[text[2]])
				except Exception:
					return (-1, 'Неподдерживаемый формат запроса')
			else:
				return (-1, 'Неподдерживаемый формат запроса')

		elif len(text) == 4:
			if 'в' in text or 'вo' in text:
				week_day = Parser.weekdays[text[2]]
				today = date.today().weekday()

				shift = week_day - today + (7 if (week_day - today <= 0) else 0)
				try:
					return (text[0], shift, Parser.daytimes[text[3]])
				except Exception:
					return (-1, 'Неподдерживаемый формат запроса')

			elif 'через' in text:
				try:
					return (text[0], int(text[2]), 'day')
				except Exception:
					return (-1, 'Неподдерживаемый формат запроса')
			else:
				return (-1, 'Неподдерживаемый формат запроса')

		elif len(text) == 5:
			try:
				return (text[0], int(text[3]), Parser.daytimes[text[1]])
			except Exception:
				return (-1, 'Неподдерживаемый формат запроса')
		else:
			return (-1, 'Неподдерживаемый формат запроса')
