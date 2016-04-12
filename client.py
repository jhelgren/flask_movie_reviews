# Jason Helgren
# MSAN 697 Final Project
# jhelgren@gmail.com

import httplib

# Development server - change to AWS for production.
SERVER = 'localhost:5000'


def get_total_count():
    """Get the total number of movies in the database."""
    
    out = dict()
    h = httplib.HTTPConnection(SERVER)
    h.request('GET', 'http://'+SERVER+'/count')
    resp = h.getresponse()
    out = resp.read()
    return out

def get_movies_by_year(year):
    """Get the list of movies for a given year."""

    out = dict()
    h = httplib.HTTPConnection(SERVER)
    h.request('GET', 'http://'+SERVER+'/year/'+str(year))
    resp = h.getresponse()
    out = resp.read()
    return out

def get_movies_by_castcrew(role, name):
    """
    Get the list of movies associated with a given role and name.

    Keywork arguments:
    role - the role of ther person of interest, e.g. actor or director.
    name - the name of the person of interest.
    """

    out = dict()
    h = httplib.HTTPConnection(SERVER)
    h.request('GET', 'http://'+SERVER+'/people/'+role+'/'+name)
    resp = h.getresponse()
    out = resp.read()
    return out

def get_top_movies(n):
    """
    Get a list of the best movies, as ranked by their count of positive reviews.

    Keywork arguments:
    n: how many movies to include in the list.
    """

    out = dict()
    h = httplib.HTTPConnection(SERVER)
    h.request('GET', 'http://'+SERVER+'/most_positive/'+str(n))
    resp = h.getresponse()
    out = resp.read()
    return out

def get_sentiment(title, sentiment, review):
    """
    Use the sentiment analyzer to determine the sentiment of the review.

    Keywork arguments:
    title: the movie title.
    sentiment: the sentiment of the review as determined by the submitter.
    review: the text of the review.
    """

    out = dict()
    h = httplib.HTTPConnection(SERVER)
    h.request('GET', 'http://'+SERVER+'/sentiment/'+title+'/'+sentiment+'/'+review)
    resp = h.getresponse()
    out = resp.read()
    return out


if __name__ == '__main__':
    print "************************************************"
    print "test of my flask app running at ", SERVER
    print "created by Jason Helgren"
    print "************************************************"
    print " "
    print "******** total movies in the database **********"
    print get_total_count()
    print " "
    print "******* list of movies released in 1997 ********"
    print get_movies_by_year(1997)
    print " "
    print "**** list of movies for actor Jason Helgren ****"
    print get_movies_by_castcrew('actor', 'Jason%20Helgren')
    print " "
    print "************ list of top 3 movies **************"
    print get_top_movies(3)
    print " "
    print "******* get sentiment for a bad review *********"
    review_neg = 'Terrible%20movie.%20Perhaps%20the%20worst%20Ive%20seen.'
    print get_sentiment('Bad%20Movie', 'neg', review_neg)
    print " "
    print "******* get sentiment for a good review ********"
    review_pos = 'I%20loved%20this%20movie.%20It%20was%20an%20excellent%20film'
    print get_sentiment('Good%20Movie', 'pos', review_pos)

