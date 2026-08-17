from flask import Flask
from scraper import scrape_rss  # I-import mo yung function galing sa scraper mo

app = Flask(__name__)

@app.route("/")
def home():
    # Pwede mo rin tawagin o i-trigger dito kung gusto mo, o kaya ay i-import lang ang function
    return scrape_rss()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
