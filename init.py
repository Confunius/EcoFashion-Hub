from flask import Flask, render_template, request, redirect, url_for
import shelve

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/products')
def products():
    return render_template('Product.html')

@app.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')

@app.route('/CustomerService')
def CustomerService():
    return render_template('CustomerService.html')

@app.route('/ServiceRecord')
def ServiceRecord():
    return render_template('ServiceRecord.html')
    
if __name__ == '__main__':
    app.run()
