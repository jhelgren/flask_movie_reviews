## Flask Demo with a Database of Movie Reviews

This code creates a database of movies and reviews, which can be queried with a web browser. The code uses three data sources to generate a mock data set:

* people.txt: a file with people.
* titles.csv: a file with movies and release year.
* txt_sentoken: movie reviews from Bo Pang and Lillian Lee's [movie review data set](https://www.cs.cornell.edu/people/pabo/movie-review-data/).

The code also requires a Postgres server with a database called "movies_nosql". To use this code, first run data_loader.py to read each of the data sources and populate the Postgres database. Then run server.py. To test the server, either run client.py or point a web browser to http://localhost:5000/. Consult client.py for possible queries. For example, to find the number of movies in the database, change the address to http://localhost:5000/count.


