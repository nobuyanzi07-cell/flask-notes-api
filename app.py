from functools import wraps

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import api, app, db
from models import Note, User

MAX_PER_PAGE = 50


def error(messages, status):
    """Error body in the shape the client expects: {"errors": [...]}."""
    if isinstance(messages, str):
        messages = [messages]
    return {"errors": messages}, status


def login_required(func):
    """Reject requests that have no logged-in user in the session."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return error("Unauthorized", 401)
        return func(*args, **kwargs)

    return wrapper


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        confirmation = data.get("password_confirmation")

        errors = []
        if not username:
            errors.append("Username is required")
        if not password:
            errors.append("Password is required")
        if confirmation is not None and confirmation != password:
            errors.append("Password confirmation does not match")
        if errors:
            return error(errors, 422)

        user = User(username=username)
        user.password_hash = password
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return error("Username already taken", 422)

        session["user_id"] = user.id
        return user.to_dict(), 201


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        user = User.query.filter_by(username=data.get("username")).first()

        if user and user.authenticate(data.get("password") or ""):
            session["user_id"] = user.id
            return user.to_dict(), 200
        return error("Invalid username or password", 401)


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None
        if user:
            return user.to_dict(), 200
        return error("Unauthorized", 401)


class NoteList(Resource):
    method_decorators = [login_required]

    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), MAX_PER_PAGE)

        pagination = (
            Note.query.filter_by(user_id=session["user_id"])
            .order_by(Note.created_at.desc(), Note.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return {
            "notes": [n.to_dict() for n in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    def post(self):
        data = request.get_json() or {}
        title = (data.get("title") or "").strip()
        if not title:
            return error("Title is required", 422)

        note = Note(
            title=title,
            content=data.get("content") or "",
            user_id=session["user_id"],
        )
        db.session.add(note)
        db.session.commit()
        return note.to_dict(), 201


class NoteDetail(Resource):
    method_decorators = [login_required]

    def _get_own_note(self, note_id):
        # Filtering by user_id means other users' notes simply return 404.
        return Note.query.filter_by(id=note_id, user_id=session["user_id"]).first()

    def patch(self, note_id):
        note = self._get_own_note(note_id)
        if not note:
            return error("Note not found", 404)

        data = request.get_json() or {}
        if "title" in data:
            title = (data["title"] or "").strip()
            if not title:
                return error("Title cannot be empty", 422)
            note.title = title
        if "content" in data:
            note.content = data["content"] or ""

        db.session.commit()
        return note.to_dict(), 200

    def delete(self, note_id):
        note = self._get_own_note(note_id)
        if not note:
            return error("Note not found", 404)

        db.session.delete(note)
        db.session.commit()
        return {}, 204


api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")
api.add_resource(NoteList, "/notes")
api.add_resource(NoteDetail, "/notes/<int:note_id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)