from flask import Flask, abort, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql://root:kanunviolon@localhost/soa_app'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Task Management Application</h1>'''

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique= True, nullable = False)
    email = db.Column(db.String(120), unique=True, nullable= False)
    password = db.Column(db.String(60), nullable= False)


@app.route("/api/users/register",methods = ['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User (username = data['username'], email = data['email'], password = hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"User registered successfully"}), 201

@app.route("/api/users/get_users",methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]

    return {"users": user_list}

@app.route("/api/users/profile/<int:user_id>",methods=['GET'])
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"username":user.username, "email":user.email}), 200


@app.route("/api/users/login",methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email = data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message":"Login successful","user_id":user.id}), 200
    else:
        return jsonify({"message":"Invalid email or password"}), 401
    
@app.route("/api/users/update_user/<int:user_id>",methods=['POST'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.username = data.get('username',user.username)
    user.email = data.get('email',user.email)
    user.password = data.get('password',user.password)
    db.session.commit()
    return jsonify({"message":"User updated successfully"}), 200


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