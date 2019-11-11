from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/')
def index():
    return redirect('/snapshot/')

@app.route('/snapshot/')
def view_snap():
    return render_template('snap.html')

@app.route('/compare/')
def view_compare():
    return render_template('compare.html')

@app.route('/primitive_validation/')
def view_primitive_validation():
    return render_template('primitive_validation.html')

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
