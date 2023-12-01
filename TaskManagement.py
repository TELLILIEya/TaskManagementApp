from flask import Flask, abort, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user



app = Flask(__name__)
login_manager = LoginManager(app)

app.config['SECRET_KEY'] = 'my_key'

app.config['SQLALCHEMY_DATABASE_URI']= 'mysql://root:kanunviolon@localhost/soa_app'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

@app.route('/', methods=['GET'])
def home():
    return  render_template('accueil.html')


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique= True, nullable = False)
    email = db.Column(db.String(120), unique=True, nullable= False)
    password = db.Column(db.String(60), nullable= False)

@login_manager.user_loader
def load_user(user_id):
    # Implémentez cette fonction pour charger un utilisateur à partir de l'ID
    return User.query.get(int(user_id))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        email = request.form['email']
        user = User (username = username, email = email, password = hashed_password)
        db.session.add(user)
        db.session.commit()       
        return redirect(url_for('login'))
    return render_template('accueil.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        password = request.form['password']
        email = request.form['email']
        user = User.query.filter_by(email = email).first()
       
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')




@app.route("/api/users/profile/<int:user_id>",methods=['GET'])
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"username":user.username, "email":user.email}), 200


@app.route("/api/users/get_users",methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]

    return {"users": user_list}


@login_required   
@app.route("/api/users/update_user/<int:user_id>",methods=['POST'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username',user.username)
    user.email = data.get('email',user.email)
    user.password = data.get('password',user.password)
    db.session.commit()
    return jsonify({"message":"User updated successfully"}), 200

@login_required
@app.route("/api/users/delete_user/<int:user_id>",methods = ['GET','DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return {"message": f"User with ID {user_id} deleted successfully"}, 200
    else:
        return jsonify({"message": f"User with ID {user_id} not found"}), 404
    

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text)
    deadline = db.Column(db.Date)
    completed = db.Column(db.Boolean, default =False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable = False)

@app.route("/api/tasks",methods= ['POST'])
def create_task():
    data = request.get_json()
    task = Task(title = data['title'], description = data.get('description'),deadline = data.get('deadline'), user_id = data['user_id'])
    db.session.add(task)
    db.session.commit()
    return jsonify({"message":"Task created successfully"}), 201

@app.route("/api/tasks/<int:task_id>",methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title = data.get('title',task.title)
    task.description = data.get('description',task.description)
    task.deadline = data.get('deadline',task.deadline)
    db.session.commit()
    return jsonify({"message":"Task updated successfully"}), 200

@app.route("/api/tasks/<int:task_id>/completed",methods=['PATCH'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return jsonify({"message":"Task marked as completed"}),200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()