"""Flask server instance."""
from flask import Flask

app = Flask(__name__)


@app.route('/')
def check():
    """Display a Rocket status image."""
    return "🚀"
