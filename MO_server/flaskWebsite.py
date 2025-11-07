from flask import Flask, render_template, jsonify
app = Flask(__name__, template_folder="Frontend")

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/data', methods = ['GET', 'POST'])
def api():
    if(request.method == 'GET'):

        data = "hello world"
        return jsonify({'data': data})