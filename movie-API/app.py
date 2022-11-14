from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlit")

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, unique=True, nullable=False)
    genre = db.Column(db.String, nullable=True)
    mpaa_rating = db.Column(db.String)
    movie_img = db.Column(db.String, unique=True)
    all_reviews = db.relationship('Review', backref='movie', cascade='all, delete, delete-orphan', lazy=True)

    def __init__(self, title, genre, mpaa_rating, movie_img):
        self.title = title 
        self.genre = genre 
        self.mpaa_rating = mpaa_rating 
        self.movie_img = movie_img 

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    star_rating = db.Column(db.Float, nullable=False)
    review_text = db.Column(db.Text(300))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    def __init__(self, star_rating, review_text, movie_id):
        self.star_rating = star_rating
        self.review_text = review_text
        self.movie_id = movie_id

class ReviewSchema(ma.Schema):
    class Meta:
        fields = ('id', 'star_rating', 'review_text', 'movie_id')

review_schema = ReviewSchema()
many_review_schema = ReviewSchema(many=True)

class MovieSchema(ma.Schema):
    all_reviews = ma.Nested(many_review_schema)
    class Meta:
        fields = ('id', 'title', "genre", 'mpaa_rating', 'movie_img', 'all_reviews')

movie_schema = MovieSchema()
many_movie_schema = MovieSchema(many=True)

@app.route('/movie/add', methods=["POST"])
def add_movie():
    if request.content_type != 'application/json':
        return jsonify("Error: Data must be sent asd JSON or NOGO!")

    post_data = request.get_json()
    title = post_data.get('title')
    genre = post_data.get('genre')
    mpaa_rating = post_data.get('mpaa_rating')
    movie_img = post_data.get('moive_img')

    if title == None:
        return jsonify('Error: Title is required')
    
    if genre == None:
        return jsonify('Error: Genre is required')

    new_movie = Movie(title, genre, mpaa_rating, movie_img)
    db.session.add(new_movie)
    db.session.commit()

    return jsonify(movie_schema.dump(new_movie))

@app.route('/movie/get')
def get_movies():
    all_movies = db.session.query(Movie).all()
    return jsonify(many_movie_schema.dump(all_movies))

@app.route('/movie/get/<id>')
def get_one_movie(id):
    one_movie = db.session.query(Movie).filter(Movie.id  == id).first()
    return jsonify(movie_schema.dump(one_movie))

@app.route('/movie/edit/<id>', methods=["POST"])
def edit_movie(id):
    if request.content_type != 'application/json':
        return jsonify('Error: Send Data as Json')

    put_data = request.get_json()
    title = put_data.get('title')
    genre = put_data.get('genre')
    mpaa_rating = put_data.get('mpaa_rating')
    movie_img = put_data.get('movie_img')


    edit_movie = db.session.query(Movie).filter(Movie.id == id).first()

    if title != None:
        edit_movie.title = title
    if genre != None:
        edit_movie.genre = genre
    if mpaa_rating != None:
        edit_movie.mpaa_rating = mpaa_rating
    if movie_img != None:
        edit_movie.movie_img = movie_img

    db.session.commit()

    return jsonify(movie_schema.dump(edit_movie))

@app.route('/movie/delete/<id>', methods=["DELETE"])
def delete_movie(id):
    delete_movie = db.session.query(Movie).filter(Movie.id == id).first()
    db.session.delete(delete_movie)
    db.session.commit()

    return jsonify('Movie Has Been Deleted')

@app.route('/movie/add/many', methods=["Post"])
def add_many_movies():
    if request.content_type != "application/json":
        return jsonify("Error: Send Data as Json to Proceed")

    post_data = request.get_json()
    movies = post_data.get("movies")

    new_movies = []

    for movie in movies:
        title = movie.get('title')
        genre = movie.get('genre')
        mpaa_rating = movie.get('mpaa_rating')
        movie_img = movie.get('movie_img')


        existing_movie_check = db.session.query(Movie).filter(Movie.title == title).first()
        if existing_movie_check is None:
            new_movie = Movie(title, genre, mpaa_rating, movie_img)
            db.session.add(new_movie)
            db.session.commit()
            new_movies.append(new_movie)

    return jsonify(many_movie_schema.dump(new_movies))


@app.route('/review/add', methods=["POST"])
def add_review():
    if request.content_type != 'application/json':
        return jsonify("Review has been submitted")

    post_data = request.get_json()
    star_rating = post_data.get('star_rating')
    review_text = post_data.get('review_text')
    movie_id = post_data.get('movie_id')
    
    if star_rating == None:
        return jsonify("Error: Star rating required in order to submit")
    if movie_id == None:
        return jsonify("Error: Movie ID required in order to submit")

    new_review = Review(star_rating, review_text, movie_id)
    db.session.add(new_review)
    db.session.commit()

    return jsonify(review_schema.dump(new_review))
    






if __name__ == '__main__':
    app.run(debug=True)