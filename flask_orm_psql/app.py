from flask import abort, jsonify, redirect, render_template, request, url_for
from flask_migrate import Migrate
import sys

from init import create_app
from models import db, TodosList, Todo

app = create_app()
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    return redirect(url_for("get_todos_from_list", list_id=1))


# JSON
@app.route("/lists", methods=["POST"])
def create_list():
    response_body = {}
    error = False
    try:
        name = request.get_json()["name"]
        list_in = TodosList(name=name)
        response_body["msg"] = "todos list has been created"
        db.session.add(list_in)
        db.session.commit()
        response_body["id"] = list_in.id
        response_body['name'] = list_in.name
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify(response_body)


# web
@app.route("/lists/<list_id>")
def get_todos_from_list(list_id):
    active_list = TodosList.query.get(list_id)
    active_list_todos = Todo.query.filter_by(list_id=list_id).order_by(
        Todo.id
    ).all()
    listsData = []
    lists = TodosList.query.order_by(TodosList.id).all()
    for list in lists:
        todos = list.todos
        list_completed = len(todos) > 0
        for todo in todos:
            if not todo.completed:
                list_completed = False
                break
        listsData.append({
            "data": list,
            "completed": list_completed
        })
    return render_template(
        "index.html",
        active_list=active_list,
        active_listId=list_id,
        active_list_todos=active_list_todos,
        lists=listsData
    )


# JSON
@app.route("/lists/<list_id>/todos")
def get_todos_from_list_json(list_id):
    active_list_todos = Todo.query.filter_by(list_id=list_id).order_by(
        Todo.id
    ).all()
    response_body = {}
    response_body["msg"] = "fetched all todos for list " + list_id
    response_body["data"] = []
    for todo in active_list_todos:
        response_body["data"].append({
            "id": todo.id,
            "completed": todo.completed
        })
    return jsonify(response_body)


# JSON
@app.route("/todos", methods=["POST"])
def create_todo():
    response_body = {}
    error = False
    try:
        description = request.get_json()["description"]
        list_id = request.get_json()["list_id"]
        todo = Todo(description=description)
        list = TodosList.query.get(list_id)
        todo.list = list
        response_body["msg"] = "todo has been created"
        db.session.add(todo)
        db.session.commit()
        response_body["id"] = todo.id
        response_body['description'] = todo.description
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify(response_body)


# JSON
@app.route("/lists/<int:id>", methods=["DELETE"])
def delete_list(id):
    response_body = {}
    error = False
    try:
        Todo.query.filter_by(list_id=id).delete()
        TodosList.query.filter_by(id=id).delete()
        db.session.commit()
        response_body['msg'] = "todos list has been deleted !"
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify(response_body)


# JSON
@app.route("/todos/<int:id>", methods=["DELETE"])
def delete_todo(id):
    response_body = {}
    error = False
    try:
        Todo.query.filter_by(id=id).delete()
        db.session.commit()
        response_body['msg'] = "todo has been deleted !"
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify(response_body)


# JSON
@app.route('/lists/<int:list_id>/complete', methods=['PUT'])
def update_list(list_id):
    response_body = {}
    error = False
    try:
        completed = request.get_json()['completed']
        todos = Todo.query.filter_by(list_id=list_id).order_by(Todo.id).all()
        for todo in todos:
            todo.completed = completed
        db.session.commit()
        response_body['msg'] = "list " + str(list_id) + " completed updated"
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify(response_body)


# JSON
@app.route('/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    response_body = {}
    error = False
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(id)
        todo.completed = completed
        db.session.commit()
        response_body['msg'] = "todo " + str(todo.id) + " completed updated"
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            abort(400)
        else:
            return jsonify(response_body)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
