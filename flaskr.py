# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, send_from_directory
from contextlib import closing
from werkzeug import secure_filename

# general configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# file upload configuration
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['md'])

# create flask app
app = Flask(__name__)
app.config.from_object(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Possibly not needed - need to check

# Define helper functions
def allowed_file(filename):
  return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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
@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    file = request.files['infile']
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return redirect(url_for('uploaded_file',
                      filename=filename))
  return render_template('markdown_form.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'],
                            filename)


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
