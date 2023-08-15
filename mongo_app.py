from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import re
 
app = Flask(__name__)

app.secret_key = 'xyzsdfg'

# Initialize MongoDB client
client = MongoClient("mongodb+srv://cody:team2password@books.ondwxvg.mongodb.net/")
db = client.get_database("bookstore")
users_collection = db.users
books_collection = db.book

@app.route('/index')
def index():
    return render_template('index.html')
 
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email, 'password': password})
        if user:
            session['loggedin'] = True
            session['userid'] = str(user['_id'])
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return render_template('user.html', mesage=mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage=mesage)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods=['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        account = users_collection.find_one({'email': email})
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            users_collection.insert_one({'name': userName, 'email': email, 'password': password})
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage=mesage)

@app.route("/search_results", methods=["GET"])
def search_results():
    search_term = request.args.get('searchTerm')
    category = request.args.get('category')
    
    # Build the MongoDB query based on search_term and category (if provided)
    query = {}
    if search_term:
        query["$or"] = [
            {"title": {"$regex": search_term, "$options": "i"}},
            {"author": {"$regex": search_term, "$options": "i"}},
            {"isbn": {"$regex": search_term, "$options": "i"}}
        ]
    if category:
        query["category"] = category
    
    # Retrieve book data from MongoDB based on the query
    #books_collection = db['book']  # Replace 'books' with your collection name
    books = books_collection.find(query)
    
    return render_template("search_results.html", books=books)
   
if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)