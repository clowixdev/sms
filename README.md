# Shipment Management Service (SMS 🚚)

## About

**Shipment management system (SMS 🚚)** is a service that is created to help drivers exclude paper **documents 📋** which can be damaged or lost. Manager create shipment in service, **QR-code 📲** is being sent to driver and this QR-code contains all needed information and documents in **secured 🔐** digital format. After shipment is received by endpoint, they can **"Accept shipment 🔄"** and change shipment status to **"Delivered ✅".**

## Installation

To launch project locally, you need to prepare environment for the project, i'm using `pyenv`

```console
pyenv install 3.9.20
cd </project/folder>
pyenv local 3.9.20
pyenv exec python -m venv .venv
source .venv/bin/activate(.fish) # if you using fish console
pip install -r requirements.txt
```

## TODO

1. Check all the bugs around mysql database invocation
