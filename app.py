from src import app, db
from src.models import Driver, Car, Shipment, Company

if __name__ == '__main__':
    app.run(debug=True)