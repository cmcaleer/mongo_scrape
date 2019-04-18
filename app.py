from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/marsDB")


# Route to render index.html template using data from Mongo
@app.route("/")
def home():

    # Find one record of data from the mongo database
    scrape_data = mongo.db.scraped_data.find_one()

    # Return template and data
    return render_template("index.html", scrape_data= scrape_data)


# Route that will trigger the scrape function
@app.route("/scrape")
 
def scrape():
    "Main scrape functiona that will execute all other functions" 
    "and return a dictionary"

     # Run the scrape function
    mars_data = scrape_mars.scrape_info()

    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)