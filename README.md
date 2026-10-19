# Notes API

A Flask REST API with session-based authentication. Users can sign up, log in, and manage their own private notes (full CRUD with pagination). Users can never view or modify each other's notes.

## Installation

```bash
git clone <your-repo-url>
cd <repo>
pipenv install
pipenv shell
export FLASK_APP=app.py
flask db init
flask db migrate -m "initial"
flask db upgrade
python seed.py
```

## Run

```bash
python app.py
```

The API runs at http://localhost:5555.

## Endpoints

### Auth
| Method | Route | Description |
|---|---|---|
| POST | `/signup` | Create a user and log in. Body: `username`, `password`. 201, or 422 on invalid/duplicate. |
| POST | `/login` | Log in. Body: `username`, `password`. 200, or 401 on bad credentials. |
| DELETE | `/logout` | Clear the session. 204. |
| GET | `/check_session` | Return the logged-in user. 200, or 401 if not logged in. |

### Notes (login required, 401 otherwise)
| Method | Route | Description |
|---|---|---|
| GET | `/notes?page=1&per_page=10` | Paginated list of the current user's notes. |
| POST | `/notes` | Create a note. Body: `title`, `content`. 201, or 422 if title missing. |
| PATCH | `/notes/<id>` | Update `title` and/or `content` of your own note. 404 if not found or not yours. |
| DELETE | `/notes/<id>` | Delete your own note. 204, or 404. |