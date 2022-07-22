from flask import Flask, request, render_template, jsonify, url_for, make_response, redirect, flash
from dotenv import load_dotenv
from tools import queryIndex, updateIndex
import os, requests 
from dotenv import load_dotenv

application = Flask(__name__)

load_dotenv()



@application.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@application.route('/search', methods=['POST'])
def search():

    query =  request.form.get('query')
    results = queryIndex(query)

    return render_template('search.html', results=results)
  
  
@application.route('/update', methods=['GET'])
def update():

    data = updateIndex()

    if data == True:
       flash("Index updated successfully", 'fwhite')
    else:
       flash("Index update failed", 'fred')
    
    return redirect(url_for('index'))


if __name__ == "__main__":
   application.run(host='0.0.0.0', debug=True)






