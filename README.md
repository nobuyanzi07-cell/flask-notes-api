# Notes API

A Flask REST API with session-based authentication. Users can sign up, log in, and manage their own private notes with full CRUD and pagination. Users can never view or modify each other's notes. Built to work with the provided `client-with-sessions` React frontend.

## Requirements

- Python 3.8
- Pipenv

## Installation

```bash
git clone https://github.com/nobuyanzi07-cell/flask-notes-api.git
cd flask-notes-api
pipenv install
pipenv shell
export FLASK_APP=app.py
flask db upgrade
python seed.py
```

If the `migrations/` folder does not exist, run `flask db init` and `flask db migrate -m "initial"` before `flask db upgrade`.

The seed script creates three users (`user1`, `user2`, `user3`), each with 15 notes. All passwords are `password123`.

## Running the app

```bash
python app.py
```

The API runs at http://localhost:5555.

To use the frontend, run this in a second terminal:

```bash
cd client-with-sessions
npm install
npm start
```

The client runs at http://localhost:4000 and proxies requests to the API.

## Project structure

- `app.py` - routes and resources
- `config.py` - app, database, Bcrypt and API setup
- `models.py` - `User` and `Note` models
- `seed.py` - sample data
- `migrations/` - Flask-Migrate database migrations

## Endpoints

Errors are returned as `{"errors": ["message"]}`.

### Authentication

| Method | Route | Description |
|---|---|---|
| POST | `/signup` | Create a user and log them in. Body: `username`, `password`, optional `password_confirmation`. Returns 201, or 422 if invalid or the username is taken. |
| POST | `/login` | Log in. Body: `username`, `password`. Returns 200, or 401 for bad credentials. |
| DELETE | `/logout` | Clear the session. Returns 204. |
| GET | `/check_session` | Return the logged-in user. Returns 200, or 401 if not logged in. |

### Notes

All notes routes require login and return 401 otherwise.

| Method | Route | Description |
|---|---|---|
| GET | `/notes?page=1&per_page=10` | Paginated list of the current user's notes. Returns `notes`, `page`, `per_page`, `total`, `pages`. `per_page` is capped at 50. |
| POST | `/notes` | Create a note. Body: `title` (required), `content`. Returns 201, or 422 if the title is missing. |
| PATCH | `/notes/<id>` | Update `title` and/or `content` of your own note. Returns 200, or 404 if the note does not exist or belongs to another user. |
| DELETE | `/notes/<id>` | Delete your own note. Returns 204, or 404. |

## Models

- **User**: `id`, `username` (unique), hashed password (Flask-Bcrypt)
- **Note**: `id`, `title`, `content`, `created_at`, `user_id` (foreign key to User)