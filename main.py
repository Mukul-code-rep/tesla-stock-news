import os
import requests
import datetime as dt
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API = os.environ.get('S_API')
NEWS_API = os.environ.get('N_API')
account_sid = os.environ.get('SID')
auth_token = os.environ.get('TOKEN')

parameters = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK,
    'apikey': STOCK_API
}

response = requests.get(url='https://www.alphavantage.co/query', params=parameters)
response.raise_for_status()
stock_data = response.json()

today_date = dt.date.today()
yesterday_date = today_date - dt.timedelta(days=1)
day_before_yesterday = today_date - dt.timedelta(days=2)

current_value = float(stock_data['Time Series (Daily)'][str(yesterday_date)]['4. close'])
previous_value = float(stock_data['Time Series (Daily)'][str(day_before_yesterday)]['4. close'])

diff = current_value - previous_value
if diff < 0:
    percent = round(-diff / current_value * 100, 2)
else:
    percent = round(diff / current_value * 100, 2)

if percent >= 5:
    parameters = {
        'q': 'tesla',
        'from': str(yesterday_date),
        'sortBy': 'publishedAt',
        'apikey': NEWS_API
    }
    response = requests.get(url='https://newsapi.org/v2/everything', params=parameters)
    response.raise_for_status()
    news_data = response.json()
    top_news = news_data['articles'][:3]

    client = Client(account_sid, auth_token)

    if diff < 0:
        message = client.messages.create(body=f"TSLA: 🔻{percent}%\n"
                                              f"Headline: {top_news[0]['title']}\nBrief: {top_news[0]['description']}\n"
                                              f"Headline: {top_news[1]['title']}\nBrief: {top_news[1]['description']}\n"
                                              f"Headline: {top_news[2]['title']}\nBrief: {top_news[2]['description']}\n",
                                         from_='+14352721610',
                                         to=os.environ.get('my_number'))
    else:
        message = client.messages.create(body=f"TSLA: 🔺{percent}%\n"
                                              f"Headline: {top_news[0]['title']}\nBrief: {top_news[0]['description']}\n"
                                              f"Headline: {top_news[1]['title']}\nBrief: {top_news[1]['description']}\n"
                                              f"Headline: {top_news[2]['title']}\nBrief: {top_news[2]['description']}\n",
                                         from_='+14352721610',
                                         to=os.environ.get('my_number'))

    print(message.status)

else:
    print("Percent change isn't high enough")
