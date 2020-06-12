import pyowm
from Keys import open_weather_api
from myweather import weather_status

owm = pyowm.OWM(open_weather_api)
observation = owm.weather_at_place('Taipei')
w = observation.get_weather()
temp = w.get_temperature('celsius')
status = w.get_detailed_status()
icon = w.get_weather_icon_url()

print(int(temp['temp']))
print(status)
print(weather_status[status])
print(icon)
