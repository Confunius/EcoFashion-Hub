from flask import Flask, render_template, request, redirect, url_for
import shelve

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/products')
def products():
    return render_template('Product.html')
if __name__ == '__main__':
    app.run()