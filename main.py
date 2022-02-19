#Johansen Data - et jonas johansen produkt | WEBFLIX V5
from flask import Flask, render_template, request, url_for, redirect, flash
from tmdbv3api import TMDb, Movie
from flask_paginate import Pagination, get_page_parameter
from werkzeug.utils import secure_filename
from tmdbv3api import Account
from tmdbv3api import Authentication
import os



tmdb = TMDb()
tmdb.api_key = '672700e3d4dd3246c3c060a7ee138222'

tmdb.language = 'en' # vil etterhvert bli styrt av account systemet. kommer i V7.

movie = Movie()

app = Flask(__name__, static_url_path='/static')


app.config['MAX_CONTENT_LENGTH'] = 900040 * 900000
app.config['UPLOAD_EXTENSIONS'] = ['.mp4']
app.config['UPLOAD_PATH'] = 'static/filmer'

# Sørger for at filtype er rett - laget for /Leggtil delen
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Hjem siden - lister populære filmer. 
@app.route('/Hjem', methods=['GET'])
def popular():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    popular_movies = movie.popular(page)
    pagination = Pagination(page=page, total=450)
    return render_template('hjem.html', Movies=popular_movies, pagination=pagination)

#Film beskrivelse
@app.route('/Movie_Detail', methods=['GET'])
def filmdesc():
    movie_id = request.args.get('id')
    m = movie.details(movie_id)
    crews = movie.credits(movie_id)
    s = movie.similar(movie_id)
    from pathlib import Path
    path_to_file = 'static/filmer/' + movie_id + '.mp4'
    path = Path(path_to_file)
    if path.is_file():
        filmeksistanse = "Se filmen"
        Flink = "/Avspiller?id=" + movie_id
    else:
        filmeksistanse = "Ikke tilgjengelig"
        Flink = ""
    if len(movie.videos(movie_id)) != 0:
        return render_template('filmen.html', Movies=m, Crews=crews,
                               youtube=movie.videos(movie_id)[0].get("key"), Similar=s, filmeksistanse=filmeksistanse, Flink=Flink)
    else:
        return render_template('filmen.html', Movies=m, Crews=crews,
                               youtube="", Similar=s, filmeksistanse=filmeksistanse, Flink=Flink)

#Avspilleren for filmer
@app.route('/Avspiller', methods=['GET'])
def avspiller():
    movie_id = request.args.get('id')
    m = movie.details(movie_id)
    return render_template('filmviewer.html', Movies=m)

#Søks funksjonen
@app.route('/Search', methods=['GET'])
def search():
    query = request.args.get('query')
    searching = movie.search(query)
    return render_template('search.html', Movies=searching)

#film adder frontenden
@app.route('/Leggtil', methods=['GET'])
def filmader():
    movie_id = request.args.get('id')
    m = movie.details(movie_id)
    return render_template('filmadder.html', Movies=m)

# Mulighet for å legge til filmer - lagres automatisk som /static/filmer/film_id.mp4 - film adder backend
@app.route('/Leggtil', methods=['GET', 'POST'])
def upload_files():
    movie_id = request.args.get('id')
    m = movie.details(movie_id)
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            filmlagttil = ("")
            filmfailed = ("Feil filtype! kun .mp4!")
            return render_template('filmadder.html', filmlagttil=filmlagttil, Movies=m, filmfailed=filmfailed)
            abort(400)
        prosfilnavn = (movie_id + '.mp4')
        filmlagttil = ("Filmen er lagt til!")
        filmfailed = ("")
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], prosfilnavn))
        return render_template('filmadder.html', filmlagttil=filmlagttil, Movies=m, filmfailed=filmfailed)
    else:
        filmlagttil = ("")
        filmfailed = ("Ingen fil? skjerp deg")
        return render_template('filmadder.html', filmlagttil=filmlagttil, Movies=m, filmfailed=filmfailed)
        
#Loginn ikke i produksjon enda, men "fungerer"
@app.route('/loginn', methods=['POST', 'GET'])
def login_render():
    return render_template('loginn.html')
#Loginn ikke i produksjon enda, men "fungerer"
@app.route('/minside', methods=['POST', 'GET'])
def login_render_post():   
    brukernavn = request.form["brukernavn"]
    passord = request.form["passord"]
    USERNAME = request.args.get("brukernavn")
    PASSWORD = request.args.get("passord")
    sesskey = "1b9a3a628a2e643aef54aca4469a6e12b33296f5"
    apikey = tmdb.api_key
    auth = Authentication(username=brukernavn, password=passord)
    account = Account()
    details = account.details()
    return render_template('minside.html', auth=auth, details=details, sesskey=sesskey, apikey=apikey)

#Radarr er i produksjon - ikke ferdigstilt, må etterhvert opprettes en webconfig for denne.
@app.route('/Radarr', methods=['GET', 'POST'])
def radarr():
    from arrapi import RadarrAPI
    baseurl = 'http://192.168.50.36:7979'
    apikey = '8a975ad8f2b3492099ddfab557d66990'
    radarr = RadarrAPI(baseurl, apikey)
    movie_id = request.args.get('id')
    movie = radarr.get_movie(tmdb_id=movie_id)
    movie.add("/filmer", "Any")
    return "", 204

if __name__ == '__main__':
    app.run(debug=True)

