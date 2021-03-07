# Toripoliisi

"Ookkonää Oolusta, pelkääkkönää polliisia"

Toripoliisi is a small application to scrape muusikoiden.net/tori (= Craigslist for Finnish 
musicians) for a given keyword and a category and send notifications via Telegram if new items
are found.

I am running it in Google Cloud Platform as a Cloud Function, triggered by a PubSub event which
in turn is scheduled with Cloud Scheduler.

Running it requires:
- A Telegram account and a bot token (talk to @BotFather to get one)
- Your Telegram account id to send messages to
- A GCP bucket to store the JSON blob
- A GCP project with cloud functions, cloud pubsub and cloud scheduler APIs enabled
