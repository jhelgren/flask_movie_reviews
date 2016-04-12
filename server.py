# Jason Helgren
# MSAN 697 Final Project
# jhelgren@gmail.com

from flask import Flask, jsonify
import psycopg2, psycopg2.extras
from sqlalchemy import create_engine

from sklearn.feature_extraction.text import CountVectorizer
from sklearn import cross_validation
from sklearn.naive_bayes import MultinomialNB

import pandas as pd
import numpy as np

# Development database - change to AWS for production.
DB_DSN = "host=localhost dbname=movies_nosql"
alchemy_url = 'postgresql+psycopg2://localhost/movies_nosql'

def db_to_reviews():
    """Copy reviews from the database into a Pandas dataframe."""
    engine = create_engine(alchemy_url)
    cols = ['review', 'sentiment']
    reviews = pd.read_sql_table('reviews', con=engine, columns = cols)
    return reviews

def add_one_review(record):
    """Insert a single record into the reviews table."""
    print record[1], type(record[1])
    print record[2], type(record[2])
    try:
       sql = "INSERT INTO reviews VALUES(%s, %s, %s)"
       conn = psycopg2.connect(dsn=DB_DSN)
       cur = conn.cursor()
       cur.executemany(sql, record)
       conn.commit()
    except psycopg2.Error as e:
       print e.message
    else:
       cur.close()
       conn.close()

app = Flask(__name__)

@app.route('/')
def default():
    output = dict()
    # nothing is going on here
    output['message'] = 'Welcome to the test app!'
    return jsonify(output)

@app.route('/count')
def movie_count():
    """Get the total number of movies in the database."""
    out = dict()
    
    try:
       sql = "SELECT sum(1) AS movie_count FROM movies"
       conn = psycopg2.connect(dsn=DB_DSN)
       cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
       cur.execute(sql)
       rs = cur.fetchone() 
       out['total_movies_in_database'] = rs['movie_count']
    except psycopg2.Error as e:
       out['exception'] = e
    else:
       cur.close()
       conn.close()

    return jsonify(out) 

@app.route('/year/<year>')
def movies_by_year(year):
    """Get the list of movies for a given year."""
    
    out = dict()
    
    try:
        sql = "SELECT title FROM movies WHERE year = %s"
        conn = psycopg2.connect(dsn=DB_DSN)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (year, ))
        rs = cur.fetchall() 
        titles = list()
        for title in rs:
            titles.append(title['title'])
        out[year] = titles

    except psycopg2.Error as e:
       out['exception'] = e
    else:
       cur.close()
       conn.close()

    return jsonify(out) 

@app.route('/people/<castcrew>/<name>')
def movies_by_role(castcrew, name):
    """Get the list of movies for a given role."""
    
    out = dict()
    
    try:
        sql = "SELECT title FROM movies WHERE castcrew->>%s = %s"
        conn = psycopg2.connect(dsn=DB_DSN)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (castcrew, name))
        rs = cur.fetchall() 
        titles = list()
        for title in rs:
            titles.append(title['title'])
        out[name] = titles

    except psycopg2.Error as e:
       out['exception'] = e
    else:
       cur.close()
       conn.close()

    return jsonify(out) 

@app.route('/most_positive/<how_many>')
def most_positive(how_many):
    """Find the movies with the how_many most postive reviews."""
    out = dict()
    
    try:
        sql = """
        SELECT title, sum(1) AS most_pos FROM reviews 
        WHERE sentiment = 'pos'
        GROUP BY title ORDER BY most_pos DESC LIMIT %s; 
        """
        conn = psycopg2.connect(dsn=DB_DSN)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (how_many,))
        rs = cur.fetchall() 
        rank = 1
        for title in rs:
            out[rank] = {'title':title['title'], 
                         'positive reviews':title['most_pos']}
            rank += 1

    except psycopg2.Error as e:
       out['exception'] = e
    else:
       cur.close()
       conn.close()

    return jsonify(out) 

@app.route('/sentiment/<title>/<sentiment>/<text>')
def sentiment_analysis(title, sentiment, text):
    """Analyze the sentiment of a provided movie review."""
    out = dict()
    out['Current accuracy'] = avg_acc
    pred = str(clf.predict(vectorizer.transform([text,]))[0])
    out['Prediction for your review'] = pred
    return jsonify(out) 


if __name__ == '__main__':
    reviews = db_to_reviews()
    text = list(reviews['review'])
    y = reviews['sentiment']
    vectorizer = CountVectorizer(min_df=1, max_features=5000, 
      stop_words = 'english')
    X = vectorizer.fit_transform(text)
    folds = 10
    k_fold = cross_validation.KFold(X.shape[0], folds, 
        shuffle=True, random_state=None)
    clf = MultinomialNB(alpha = 1.0)
    scores = list()
    for k, (train, test) in enumerate(k_fold):
        clf.fit(X[train], y[train])
        accuracy = clf.score(X[test], y[test])
        scores.append(accuracy)
    avg_acc = np.mean(scores)

    app.debug = True
    app.run() # Add host = '0.0.0.0' for production.
    
