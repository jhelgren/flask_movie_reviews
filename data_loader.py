# Jason Helgren
# MSAN 697 Final Project
# jhelgren@gmail.com

import csv
import glob
import json
import random

import pandas as pd    

import psycopg2
from sqlalchemy import create_engine
import sqlalchemy

# Development database - change to AWS for production.
DB_DSN = "host = localhost dbname = movies_nosql"
alchemy_url = 'postgresql+psycopg2://localhost/movies_nosql'

people_file = "people.txt"
title_file = "titles.csv"


def get_people(filename):
    """Get a list of people."""

    lines = [line.rstrip('\n').rstrip('\r') for line in open(filename)]
    return lines

def get_titles(filename):
    """Get a list of movies and their release year."""

    with open(filename) as f:
        reader = csv.DictReader(f, fieldnames = ['title', 'year'])
        titles = list(reader)
        return titles

def transform_data(titles, people):
    """
    Randomly match movie titles with cast and crew roles. In other words, this
    function makes up some data.

    Keyword arguments:
    titles: a list of dictionaries with movie titles and release year.
    people: a list of people to serve as cast and crew for the movie.

    Returns: a list of 
    """
    
    movies = list()

    for t in titles:
        title = t['title']
        year = t['year']
        director = random.choice(people)
        producer = random.choice(people)
        actor = random.choice(people)
        castcrew = {'director' : director, 'producer': producer, 'actor': actor}
        movies.append((title, year, json.dumps(castcrew)))

    return movies

def drop_table():
    """Drops the table 'movies' if it exists."""

    try:
       sql = "DROP TABLE IF EXISTS movies"
       conn = psycopg2.connect(dsn=DB_DSN)
       cur = conn.cursor()
       cur.execute(sql)
       conn.commit()
    except psycopg2.Error as e:
       print e.message
    else:
       cur.close()
       conn.close()

def create_table():
    """Create a table to hold movie data."""

    try:
       sql = "CREATE TABLE movies (title TEXT, year INTEGER, castcrew JSON)"
       conn = psycopg2.connect(dsn=DB_DSN)
       cur = conn.cursor()
       cur.execute(sql)
       conn.commit()
    except psycopg2.Error as e:
       print e.message
    else:
       cur.close()
       conn.close()

def insert_data(data):
    """Insert data (title, year, and cast/crew info) into the movies table."""

    try:
       sql = "INSERT INTO movies VALUES(%s, %s, %s)"
       conn = psycopg2.connect(dsn=DB_DSN)
       cur = conn.cursor()
       cur.executemany(sql, data)
       conn.commit()
    except psycopg2.Error as e:
       print e.message
    else:
       cur.close()
       conn.close()



def get_reviews(titles):
    """
    Read labeled movie reviews and randomly assign them to a title. In other 
    words, make up some data.

    Keyword arguments:
    titles: a list of dictionaries with movie titles and release year.

    Returns: a Pandas dataframe with review and title data.
    """

    neg_files = glob.glob("txt_sentoken/neg/*.txt")
    pos_files = glob.glob("txt_sentoken/pos/*.txt")
    review_dict = {'sentiment' : list(), 'review' : list(), 'title' : list()}

    for file in neg_files:
        with open(file, 'r') as f:
            review_text = f.read()
            review_dict['sentiment'].append("neg")
            review_dict['review'].append(review_text)
            review_dict['title'].append(random.choice(titles)['title'])
    for file in pos_files:
        with open(file, 'r') as f:
            review_text = f.read()
            review_dict['sentiment'].append("pos")
            review_dict['review'].append(review_text)
            review_dict['title'].append(random.choice(titles)['title'])
    reviews = pd.DataFrame(review_dict)
    return reviews

def reviews_to_db(reviews):
    table = 'reviews'
    col_types = {'sentiment' : sqlalchemy.types.CHAR(3), 
                 'review' : sqlalchemy.types.TEXT, 
                 'title' : sqlalchemy.types.TEXT}
    reviews.to_sql(table, engine, if_exists='replace', 
        index = False, dtype = col_types)



if __name__ == '__main__':
    print "Getting lists of movie titles, casts, and crews."
    titles = get_titles(title_file)
    people = get_people(people_file)

    print "Getting movie reviews."
    reviews = get_reviews(titles)

    print "Copying movie reviews to the reviews table."
    engine = create_engine(alchemy_url)
    reviews_to_db(reviews)

    print "Transforming movie data."
    movie_data = transform_data(titles, people)
    
    print "Copying movie data to the movies table."
    drop_table()
    create_table()
    insert_data(movie_data)




