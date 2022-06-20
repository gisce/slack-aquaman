import sys
from datetime import datetime
import re
import requests
import osconf
# Use the package we installed
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

slack = osconf.config_from_environment('SLACK', ['bot_token', 'signing_secret', 'app_token'])
aquaservice = osconf.config_from_environment('AQUASERVICE', ['token', 'pin', 'contract'])

# Initializes your app with your bot token and signing secret
app = App(
    token=slack['bot_token'],
    signing_secret=slack['signing_secret']
)

@app.message(re.compile(".*ltima.*(aigua|garrafa).*"))
def tens_send(message, say):
    user = message['user']
    r = requests.post(
        'https://appclient.aquaservice.com:8081/api/v3_5/delivery/next-delivery',
        json=aquaservice
    )
    if r.status_code == 200:
        next_delivery = datetime.strptime(r.json()['success']['delivery']['delivery_date'], '%Y-%m-%d')
        if (next_delivery - datetime.now()).days < 3:
            status = 'tranquil'
        else:
            status = 'oju!'
        say(f"Ep <@{user}>, tens set? {status}, la pròxima entrega d'aigua serà el {next_delivery.strftime('%Y-%m-%d')}")


# Start your app
if __name__ == "__main__":
    try:
        SocketModeHandler(app, slack['app_token']).start()
    except KeyboardInterrupt:
        sys.exit(0)
