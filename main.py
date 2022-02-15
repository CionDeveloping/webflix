#Johansen Data - et jonas johansen produkt
from flask import Flask, render_template, request
from tmdbv3api import TMDb, Movie
from flask_paginate import Pagination, get_page_parameter

tmdb = TMDb()
tmdb.api_key = '672700e3d4dd3246c3c060a7ee138222' 

tmdb.language = 'en'

movie = Movie()

app = Flask(__name__, static_url_path='/static')

@app.route('/Hjem', methods=['GET'])
def popular():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    popular_movies = movie.popular(page)
    pagination = Pagination(page=page, total=450, css_framework="bootstrap4")
    return render_template('hjem.html', Movies=popular_movies, pagination=pagination)

@app.route('/Movie_Detail', methods=['GET'])
def filmdesc():
    movie_id = request.args.get('id')
    m = movie.details(movie_id)
    crews = movie.credits(movie_id)

    if len(movie.videos(movie_id)) != 0:
        return render_template('filmen.html', Movies=m, Crews=crews,
                               youtube=movie.videos(movie_id)[0].get("key"))
    else:
        return render_template('filmen.html', Movies=m, Crews=crews,
                               youtube="")

@app.route('/Avspiller', methods=['GET'])
def avspiller():
    movie_id = request.args.get('id')
    m = movie.details(movie_id)
    return render_template('filmviewer.html', Movies=m)

@app.route('/Leggtil', methods=['GET'])
def filmader():
    movie_id = request.args.get('id')
    m = movie.details(movie_id)
    return render_template('filmadder.html', Movies=m)

@app.route('/Search', methods=['GET'])
def search():
    query = request.args.get('query')
    searching = movie.search(query)
    return render_template('search.html', Movies=searching)

if __name__ == '__main__':
    app.run(debug=True)

