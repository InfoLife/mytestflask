from flask import Flask, render_template, json, request,redirect,session
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku
import psycopg2
import os
import urlparse
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hhyywmtkdmtigu:FZC1za7z39l52c599U9LLK7UJv@ec2-107-22-170-249.compute-1.amazonaws.com:5432/dfqkjf2b19q8nc
heroku = Heroku(app)
db = SQLAlchemy(app)
app.secret_key = 'why would I tell you my secret key?'

# Create our database model
class User(db.Model):
    __tablename__ = "users"

    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))


    def __repr__(self):
        return "<User(email='%s', password='%s')>" % (
            self.email, self.password)

class UsersWish(db.Model):
    __tablename__ = "users_wish"

    def __init__(self, title=None, description = None, user = None):
        self.wish_title = wish_title
        self.wish_description = wish_description
        wish_user_id = wish_user_id

    id = db.Column(db.Integer, primary_key=True)
    wish_title = db.Column(db.String(120))
    wish_description = db.Column(db.String(120))
    wish_user_id = db.Column(db.Integer)



# Save e-mail to database
@app.route('/signUp',methods=['POST','GET'])
def signUp():
    if request.method == 'POST':
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        hashed_password = generate_password_hash(password)
        # Check that email does not already exist (not a great query, but works)
        if not db.session.query(User).filter(User.email == email).count():
            reguser = User(email, hashed_password)
            db.session.add(reguser)
            db.session.commit()
            return render_template('regok.html',regok = 'User created successfully !')
    return render_template('error.html',error = 'User Already Exists.')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    email = request.form['inputEmail']
    password = request.form['inputPassword']
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = (%s)", (email,))
    data = cursor.fetchall()
    if len(data) > 0:
        if check_password_hash(str(data[0][2]),password):
            session['user'] = data[0][0]
            return redirect('/userHome')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
    else:
        return render_template('error.html',error = 'Wrong Email address or Password.')

@app.route('/addWish',methods=['POST'])
def addWish():
    if session.get('user'):
        _title = request.form['inputTitle']
        _description = request.form['inputDescription']
        _user = session.get('user')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO users_wish(wish_title, wish_description, wish_user_id)
                      VALUES(%s,%s,%s)''', (_title, _description, _user))
        conn.commit()
        return redirect('/userHome')
    else:
        return render_template('error.html',error = 'Unauthorized Access')



@app.route('/getWish')
def getWish():
    if session.get('user'):
        _user = session.get('user')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users_wish WHERE wish_user_id = (%s)", (_user,))
        wishes = cursor.fetchall()
        wishes_dict = []
        for wish in wishes:
            wish_dict = {
                'Id': wish[0],
                'Title': wish[1],
                'Description': wish[2]}
            wishes_dict.append(wish_dict)
        return json.dumps(wishes_dict)
    else:
        return render_template('error.html', error = 'Unauthorized Access')

@app.route('/getWishById',methods=['POST'])
def getWishById():
    if session.get('user'):
        _id = request.form['id']
        _user = session.get('user')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users_wish WHERE id = (%s) AND wish_user_id = (%s)", (_id,_user))
        result = cursor.fetchall()
        wish = []
        wish.append({'Id':result[0][0],'Title':result[0][1],'Description':result[0][2]})
        return json.dumps(wish)
    else:
        return render_template('error.html', error = 'Unauthorized Access')

@app.route('/updateWish', methods=['POST'])
def updateWish():
    if session.get('user'):
        _user = session.get('user')
        _title = request.form['title']
        _description = request.form['description']
        _wish_id = request.form['id']
        cursor = conn.cursor()
        cursor.execute("UPDATE users_wish SET wish_title = %s, wish_description = %s WHERE id = %s AND wish_user_id = %s",(_title,_description,_wish_id,_user))
        conn.commit()
        return json.dumps({'status':'OK'})
    else:
        return json.dumps({'status':'Unauthorized access'})
    
@app.route('/deleteWish',methods=['POST'])
def deleteWish():
    if session.get('user'):
        _id = request.form['id']
        _user = session.get('user')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users_wish WHERE id = (%s) AND wish_user_id = (%s)", (_id,_user))
        conn.commit()
        return json.dumps({'status':'OK'})
    else:
        return render_template('error.html',error = 'Unauthorized Access')
        
    
    
@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/showAddWish')
def showAddWish():
    return render_template('addWish.html')

if __name__ == '__main__':
    #app.debug = True
    app.run()
