#!/bin/bash

source .env # service account email

gcloud functions deploy toripoliisi \
  --trigger-topic toripoliisi \
  --service-account $SERVICE_ACCOUNT_EMAIL \
  --env-vars-file .env.yaml \
  --runtime python39

gcloud scheduler jobs create pubsub toripoliisi \
  --schedule="0 9,21 * * * " \
  --topic toripoliisi \
  --message-body hello \
  --time-zone EEST
