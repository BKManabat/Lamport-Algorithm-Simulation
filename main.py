from flask import Flask, render_template, url_for, redirect
from backend import simulate
import json
import os
import glob

app = Flask(__name__)

@app.route('/')
def index():
  with open('logs.json') as f:
    logs = list(json.load(f))
  with open('references.json') as f:
    references = list(json.load(f))
  files = glob.glob('static/assets/simulation_images/*')
  return render_template("home.html", logs=logs, images=files, references = references)

@app.route('/encode/<input>')
def encode(input):
  old_files = glob.glob('static/assets/simulation_images/*')
  for f in old_files:
    os.remove(f)
  simulate(int(input))
  return redirect(url_for('index'))

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)