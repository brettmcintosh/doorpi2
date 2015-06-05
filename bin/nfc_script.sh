#!/bin/bash
#echo "{'nfcid': \"$1\"}"
curl -H "Content-Type: application/json" -X POST -d "{\"nfcid\": \"$1\"}" http://localhost:5000/api/nfc/
