from __future__ import print_function
import forecastio
import datetime
import requests
import json

print('Loading function')

# Data Params
KEY = '6e0ca338ea407af7e5961fe599eb6b09'  # weather.io api key
COORDS = (38.777140, -77.176861)
SUNNY_IMG = 'http://www.clipartbest.com/cliparts/LiK/bqA/LiKbqAzia.png'
RAINY_IMG = 'http://www.clipartkid.com/images/259/sad-rain-cloud-clip-art-free-vector-download-4v3VbO-clipart.png'
CLOUDY_IMG = 'http://matchbin-assets.s3.amazonaws.com/public/sites/275/assets/parciallycloudy_copy.jpg'
ALERTS_URL = 'https://alerts.weather.gov/cap/wwaatmget.php?x=VAC013&y=1'
SLACK_WEBHOOK_URL = ''

def lambda_handler(event, context):
    print('Checking {} at {}...'.format('weather', event['time']))

    try:
        # request
        now = datetime.datetime.now()
        forecast = forecastio.load_forecast(KEY, COORDS[0], COORDS[1], now)

        # response info
        daily = forecast.json['daily']['data'][0]
        temp_min = str(int(daily['temperatureMin'])) + 'F'
        temp_max = str(int(daily['temperatureMax'])) + 'F'
        icon = daily['icon']  # possible responses clear-day, clear-night, rain, snow, sleet, wind, fog, cloudy, partly-cloudy-day, or partly-cloudy-night
        summary = daily['summary']
        alerts = forecast.alerts()

        if 'cloudy' in icon:
            img = CLOUDY_IMG
        elif 'clear-day' in icon:
            img = SUNNY_IMG
        elif 'rain' in icon:
            img = RAINY_IMG

        # create payload
        payload = {"text": "*Weather forecast for {}*".format(now.strftime('%A, %b. %d')),
                   "channel": "#weather_bot",
                   "username": "weather-bot",
                   "icon_emoji": ":frog:",
                   "attachments": [
                       {
                           "fallback": "Weather Deats",
                           "color": 'good',
                           "text": "Summary: {} \n Low: {} \n High: {}".format(summary, temp_min, temp_max),
                           "thumb_url": img,
                       }
                   ]
        }
        if alerts:
            alert_count = len(alerts)
            alert_attachment = {
                "color": 'danger',
                "text": ":exclamation: There {} posted for this area; see <{}/|link> for details".format(
                    'is 1 alert' if alert_count == 1 else 'are {} alerts'.format(str(alert_count)), ALERTS_URL)
            }
            payload['attachments'].insert(0, alert_attachment)

        # send connect to slack
        headers = {'content-type': 'application/json'}

        session = requests.session()
        resp = session.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers, verify=False)
        print(resp)
    except Exception as e:
        print(e)
        raise e
