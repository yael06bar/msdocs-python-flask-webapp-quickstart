import os
import bson

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

#from dotenv import load_dotenv
#from flask import Flask, render_template, request
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

# access your MongoDB Atlas cluster
#load_dotenv()
connection_string: str = "mongodb+srv://victorbar40:mongodb@cluster0.tfajwbo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"#os.environ.get("CONNECTION_STRING")
mongo_client: MongoClient = MongoClient(connection_string)

# # add in your database and collection from Atlas
database: Database = mongo_client.get_database("bookshelf")
collection: Collection = database.get_collection("books")

app = Flask(__name__)

# sample code ######################################
@app.route('/')
def index2():
   print('Request for index page received')
   return render_template('index2.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))
# Sample Code #######################################

# our initial form page
#@app.route('/')  # root is "/"
#def index():
#    return render_template("index.html")


# CREATE and READ
@app.route('/books', methods=["GET", "POST"])
def books():
    if request.method == 'POST':
        # CREATE
        book: str = request.json['book']
        pages: str = request.json['pages']

        # insert new book into books collection in MongoDB
        collection.insert_one({"book": book, "pages": pages})

        return f"CREATE: Your book {book} ({pages} pages) has been added to your bookshelf.\n "

    elif request.method == 'GET':
        # READ
        bookshelf = list(collection.find())
        novels = []

        for titles in bookshelf:
            book = titles['book']
            pages = titles['pages']
            shelf = {'book': book, 'pages': pages}
            novels.insert(0, shelf)

        return novels


# UPDATE
@app.route("/books/<string:book_id>", methods=['PUT'])
def update_book(book_id: str):
   new_book: str = request.json['book']
   new_pages: str = request.json['pages']
   collection.update_one({"_id": bson.ObjectId(book_id)}, {"$set": {"book": new_book, "pages": new_pages}})

   return f"UPDATE: Your book has been updated to: {new_book} ({new_pages} pages).\n"


# DELETE
@app.route("/books/<string:book_id>", methods=['DELETE'])
def remove_book(book_id: str):
   collection.delete_one({"_id": bson.ObjectId(book_id)})

   return f"DELETE: Your book (id = {book_id}) has been removed from your bookshelf.\n"




if __name__ == '__main__':
   app.run()
