# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
# from werkzeug import secure_filename

# UPLOAD_FOLDER = '/uploads'
# ALLOWED_EXTENSIONS = set(['md'])

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Possibly not needed - need to check

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Handle database connection
def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

# Handle requests
@app.route('/')
def markdown_form():
  # cur = g.db.execute('select title, text from entries order by id desc')
  # entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
  return render_template('markdown_form.html')

@app.route('/upload', methods=['POST'])
def upload_markdown():
  print request.form['infile']
  return ""

# @app.route('/add', methods=['POST'])
# def add_entry():
#   if not session.get('logged_in'):
#     abort(401)
#   g.db.execute('insert into entries (title, text) values (?, ?)',
#                 [request.form['title'], request.form['text']])
#   g.db.commit()
#   flash('New entry was successfully posted')
#   return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
