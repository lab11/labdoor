#!/bin/bash
set -e

JTOKEN=$(curl localhost:5000/issue/dadrian)
TOKEN=$(
  echo $JTOKEN | jq -cr '.token'
)
SIG=$(
  echo $JTOKEN | jq -cr '.signature'
)

curl localhost:5000/u/${TOKEN}/${SIG}
