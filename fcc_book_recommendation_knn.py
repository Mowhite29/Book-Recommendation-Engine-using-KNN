# -*- coding: utf-8 -*-
"""fcc_book_recommendation_knn.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/github/freeCodeCamp/boilerplate-book-recommendation-engine/blob/master/fcc_book_recommendation_knn.ipynb
"""

# import libraries (you may add additional imports but you may not have to)
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, coo_matrix
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import time

# get data files
#!wget https://cdn.freecodecamp.org/project-data/books/book-crossings.zip

#!unzip book-crossings.zip

books_filename = 'BX-Books.csv'
ratings_filename = 'BX-Book-Ratings.csv'

# import csv data into dataframes
df_books = pd.read_csv(
    books_filename,
    encoding = "ISO-8859-1",
    sep=";",
    header=0,
    names=['isbn', 'title', 'author'],
    usecols=['isbn', 'title', 'author'],
    dtype={'isbn': 'str', 'title': 'str', 'author': 'str'})

df_ratings = pd.read_csv(
    ratings_filename,
    encoding = "ISO-8859-1",
    sep=";",
    header=0,
    names=['user', 'isbn', 'rating'],
    usecols=['user', 'isbn', 'rating'],
    dtype={'user': 'int32', 'isbn': 'str', 'rating': 'float32'})

# add your code here - consider creating a new cell for each section of code

def isbn_10_check(isbn):
    isbn = str(isbn)
    if not isbn[0:9].isnumeric():
        return False
    total = 0
    for i in range(0, 9, 1):
        total += (10 - i) * int(isbn[i])
    check = 11 - (total % 11)
    if check == 10:
        check = 'X'
    if check == 11:
        check = 0
    if str(check) == isbn[9]:
        return True


def isbn_13_check(isbn):
    isbn = str(isbn)
    if not isbn.isnumeric():
        return False
    total = 0
    m = 1
    for i in range(0, 12, 1):
        total += m * int(isbn[i])
        if m == 1:
            m = 3
        elif m == 3:
            m = 1
    check = 10 - (total % 10)
    if check == 10:
        check = 0   
    if str(check) == isbn[12]:
        return True
    

def book_check(isbn):
    if isbn not in books.keys():
        books[isbn] = 1
    else:
        books[isbn] = (books[isbn] + 1)


def user_check(user_id):
    if user_id not in users.keys():
        users[user_id] = 1
    else:
        users[user_id] = (users[user_id] + 1)


def isbn_validation(isbn):
    if (len(isbn) == 9) and (isbn.isnumeric()):
        return isbn
    elif (len(isbn) >= 13) and (isbn_13_check(isbn[0:13])):
        return isbn[0:13]
    elif (len(isbn) >= 10) and (isbn_10_check(isbn[0:10])):
        return isbn[0:10]
    else:
        return ''

def user_validation(user_id):
    if (int(user_id) > 0) and (int(user_id) <= 278858):
        return user_id
    else:
        return ''
    

def cleaner(entry, data):
    if data == 'books':
        valid_data = books_list
    elif data == 'users':
        valid_data = users_list

    if entry not in valid_data:
        return ''
    else:
        return entry

def title(isbn):
    for isbn_1, title in zip(df_books['isbn'], df_books['title']):
        if isbn == isbn_1:
            return title

users = {}
books = {}

#Data Cleaning
print('Identifying invalid data...')

df_ratings['isbn'] = df_ratings['isbn'].apply(isbn_validation)
df_ratings['user'] = df_ratings['user'].apply(user_validation)      
invalid_data = 0
for user_id, isbn in zip(df_ratings['user'], df_ratings['isbn']):
    if (user_id != '') and (isbn != ''):
        user_check(user_id)
        book_check(isbn)
    else:
        invalid_data += 1

print('Identifying insignificant data...') #Identifying data of no statistical significance
books_list = list(books.keys())
[books_list.remove(isbn) for isbn, count in books.items() if count < 100]

users_list = list(users.keys())
[users_list.remove(user) for user, count in users.items() if count < 200]

print('Marking data to be removed...')
df_ratings['isbn'] = df_ratings['isbn'].apply(cleaner, data='books')
df_ratings['user'] = df_ratings['user'].apply(cleaner, data='users')

print('Beginning cleaning...')
clean_data_dict = {'user': [user_id for user_id, isbn in zip(
                                        df_ratings['user'], df_ratings['isbn'])
                                        if (user_id != '') and (isbn != '')],
                   'isbn': [isbn for user_id, isbn in zip(
                                        df_ratings['user'], df_ratings['isbn'])
                                        if (user_id != '') and (isbn != '')],
                   'rating': [rating for user_id, isbn, rating in zip(
                df_ratings['user'], df_ratings['isbn'], df_ratings['rating'])
                                        if (user_id != '') and (isbn != '')]}

print('Building new database')
df_valid = pd.DataFrame(clean_data_dict)

#Retrieve title
print('Retrieving titles')

df_valid['isbn'] = df_valid['isbn'].apply(title)

df = df_valid.pivot_table(columns='user', index='isbn', values='rating', fill_value=0)
training_matrix = csr_matrix(df.values)
      
#Nearest Neighbours
print('beginning nearest neighbours')
nbrs = NearestNeighbors(metric = 'cosine', n_neighbors=5, algorithm='auto')
nbrs.fit(training_matrix)

# function to return recommended books - this will be tested
def get_recommends(book = ""):
    for index in range(len(df)):
        if df.index[index] == book:
            book = index
            break

    recommended_books = [df.index[book], []]
    distances, indices = nbrs.kneighbors(df.iloc[book,:].values.reshape(1, -1))
    
    for i in range(1, len(distances.flatten())):
        recommended_books[1].insert(0, [df.index[indices.flatten()[i]], distances.flatten()[i]])
                        
    return recommended_books

books = get_recommends("Where the Heart Is (Oprah's Book Club (Paperback))")
print(books)

def test_book_recommendation():
  test_pass = True
  recommends = get_recommends("Where the Heart Is (Oprah's Book Club (Paperback))")
  if recommends[0] != "Where the Heart Is (Oprah's Book Club (Paperback))":
    test_pass = False
  recommended_books = ["I'll Be Seeing You", 'The Weight of Water', 'The Surgeon', 'I Know This Much Is True']
  recommended_books_dist = [0.8, 0.77, 0.77, 0.77]
  for i in range(2):
    if recommends[1][i][0] not in recommended_books:
      test_pass = False
    if abs(recommends[1][i][1] - recommended_books_dist[i]) >= 0.05:
      test_pass = False
  if test_pass:
    print("You passed the challenge! 🎉🎉🎉🎉🎉")
  else:
    print("You haven't passed yet. Keep trying!")

test_book_recommendation()
