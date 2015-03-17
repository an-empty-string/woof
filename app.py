from flask import Flask, jsonify, render_template
import analyze
import wolftest
app = Flask(__name__)

@app.route('/api/wolfiness.json')
def wolfiness():
    return jsonify(users=analyze.analyze())

@app.route('/')
def index():
    return render_template('index.html')

app.run(host='0.0.0.0', port=42069, debug=False)
