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
            return redirect(url_for('task_list'))
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


@app.route("/users/delete_user",methods = ['GET','DELETE'])
@login_required
def delete_user():
    if request.method =='DELETE':
        user = User.query.get(current_user.id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html')


@login_required
@app.route("/users/update_user", methods=['GET', 'POST'])
def update_account():
    if request.method == 'POST':
        # Récupérez les données du formulaire
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('current_password')
        if not bcrypt.check_password_hash(current_user.password, password):
            return render_template("update_account.html", user=current_user, error="Incorrect current password")
        
        # Mettez à jour les informations de l'utilisateur
        current_user.username = username
        current_user.email = email

        # Appliquez les changements dans la base de données
        db.session.commit()

        # Redirigez l'utilisateur vers la page d'accueil ou une autre page après la modification
        return redirect(url_for('home'))

    return render_template("update_account.html", user=current_user)
        


"""@app.route("/api/users/profile/<int:user_id>",methods=['GET'])
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"username":user.username, "email":user.email}), 200"""


"""@app.route("/api/users/get_users",methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]

    return {"users": user_list}"""




    

class Task(db.Model):
    id_task = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text)
    deadline = db.Column(db.Date)
    completed = db.Column(db.Boolean, default =False)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),nullable = False)


@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        deadline = request.form['deadline']
        new_task = Task(title=title, description=description,deadline = deadline, id_user=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('task_list'))
    return render_template('create_task.html')

@app.route('/tasks/task_list',methods =['GET'])
@login_required
def task_list():
    tasks = Task.query.filter_by(id_user=current_user.id).all()
    return render_template('task_list.html', tasks=tasks)

"""@app.route("/api/tasks/<int:task_id>",methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title = data.get('title',task.title)
    task.description = data.get('description',task.description)
    task.deadline = data.get('deadline',task.deadline)
    db.session.commit()
    return jsonify({"message":"Task updated successfully"}), 200"""


@app.route('/tasks/completed/<int:task_id>', methods=['PUT'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return jsonify({"message":"Task marked as completed"}),200


@login_required
@app.route("/tasks/delete_task/<int:task_id>",methods = ['DELETE','GET'])
def delete_task(task_id):
    task = Task.query.get(task_id)
  
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('task_list'))
    



@login_required
@app.route("/tasks/update_task/<int:task_id>", methods=['GET', 'POST'])
def update_task(task_id):
    task = Task.query.get(task_id)

    if request.method == 'POST':
        # Récupérez les données du formulaire
        description = request.form.get('description')
        title = request.form.get('title')
        deadline = request.form.get('deadline')


        # Mettez à jour les informations de la tâche
        task.title = title
        task.description = description
        task.deadline = deadline

        # Appliquez les changements dans la base de données
        db.session.commit()

        # Redirigez l'utilisateur vers la page de liste des tâches ou une autre page après la modification
        return redirect(url_for('task_list'))

    return render_template("update_task.html", task=task)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
