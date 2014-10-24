# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, send_from_directory
from contextlib import closing
from werkzeug import secure_filename
import markdownToPDF
from datetime import date

# general configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# file upload configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['md'])

# create flask app
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

# Define helper functions
def allowed_file(filename):
  return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def convert(markdown):
  header_depth = 3
  today = date.today().strftime('%b %d, %Y')
  doc_type = 'Training documentation'
  return markdownToPDF.convert(markdown, header_depth, today, doc_type)

def render_pdf(pdf, download_filename=None):
  """Render a PDF to a response with the correct ``Content-Type`` header."""
  response = app.response_class(pdf, mimetype='application/pdf')
  if download_filename:
    response.headers.add('Content-Disposition', 'attachment',
                         filename=download_filename)
  return response

# Handle requests
@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    file = request.files['infile']
    if file and allowed_file(file.filename):
      download_filename = os.path.splitext(secure_filename(file.filename))[0]
      pdf = convert(file.stream.read())
      return render_pdf(pdf, download_filename)
  return render_template('markdown_form.html')


# DB Access examples

# @app.route('/')
# def markdown_form():
#   # cur = g.db.execute('select title, text from entries order by id desc')
#   # entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
#   return render_template('markdown_form.html')

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
