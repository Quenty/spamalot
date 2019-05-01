from flask import Flask, request, render_template, redirect, url_for, session
from uuid import uuid4
from models.Room import Room
from models.Configuration import MakeConfiguration, MakeDefaultConfiguration
import random
import app_static_routing
import os


def get_secret():
    if 'secret.txt' not in os.listdir('../'):
        open('../secret.txt', 'w').write(random_string(100))
    return open('../secret.txt').read()


# Initialize application
app = Flask(__name__)
app.secret_key = get_secret()
app_static_routing.init_routes(app)


# --- database ---
names = {}
name_last_used = {}
rooms = {}

# -
NAME_TIMEOUT = 300  # in seconds
WORDS = tuple(n.strip() for n in open(os.path.join(os.path.dirname(__file__), '../data/room_names.txt')))


def new_room_code():
    for _ in range(50):
        tentative = random.choice(WORDS)
        if rooms.get(tentative) is None:
            return tentative
    return "BEANS"


def get_user_name_from_uid(uid):
    assert(uid)

    return names.get(uid, "[Internal Error: Unknown User]")


def get_or_create_room(roomcode):
    room = rooms.get(roomcode)
    if not room:
        room = Room(session['uid'], roomcode)
        rooms[roomcode] = room

    return room


@app.before_request
def handle_uid():
    if not session.get('uid'):
        session['uid'] = uuid4()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/join', methods=['POST'])
def join_post():
    if not ('room_code' in request.form):
        return render_template('join.html', complaints=["No roomcode passed in"])

    roomcode = request.form['room_code']
    if not rooms.get(roomcode):
        return render_template('join.html', complaints=["That room does not exist"])

    room = get_or_create_room(roomcode)

    if not room.add_player(session['uid']):
        # session['complaints'] =
        print("TODO")

    return redirect(url_for('room', roomcode=roomcode))


@app.route('/room/<path:roomcode>/configure')
def configure(roomcode):
    room = get_or_create_room(roomcode)

    if not room.is_configuring():
        return redirect(url_for('room', roomcode=roomcode))

    configuration = room.get_configure() or MakeDefaultConfiguration()
    return render_template('create.html', roomcode=roomcode, **configuration)


@app.route('/room/<path:roomcode>/join')
def join_room(roomcode):
    room = get_or_create_room(roomcode)
    if not room.add_player(session['uid']):
        print("TODO")

    return redirect(url_for('room', roomcode=roomcode))


@app.route('/room/<path:roomcode>/configure', methods=['POST'])
def configure_post(roomcode):
    room = get_or_create_room(roomcode)

    if not room.is_configuring():
        return redirect(url_for('room', roomcode=roomcode))

    config = MakeConfiguration(request.form)
    if config['complaints']:
        return render_template('create.html', roomcode=roomcode, **config)

    room.set_configure(config)
    return redirect(url_for('room', roomcode=roomcode))


@app.route('/room/<path:roomcode>/rematch', methods=['POST'])
def rematch(roomcode):
    room = get_or_create_room(roomcode)
    room.rematch()
    return redirect(url_for('configure', roomcode=roomcode))


@app.route('/room/<path:roomcode>')
def room(roomcode):
    room = rooms.get(roomcode)
    if not room:
        return redirect(url_for('configure', roomcode=roomcode))

    role_info = room.get_role_info(session['uid'], get_user_name_from_uid)
    return render_template('game.html',
                           roomcode=room.get_room_code(),
                           doing_config=room.is_configuring() and get_user_name_from_uid(room.get_creator_uid()) or False,
                           is_creator=session['uid'] == room.get_creator_uid(),
                           players=room.get_player_names(get_user_name_from_uid),
                           roles=room.get_roles_data_for_rendering(),
                           status=f'{room.get_player_count()}/{room.get_max_player_count()}',
                           role_info=role_info)


@app.route('/createrandomroom')
def createrandomroom():
    roomcode = new_room_code()
    rooms[roomcode] = Room(session['uid'], roomcode)
    return redirect(url_for('configure', roomcode=roomcode))


@app.route('/room/<path:roomcode>/leave', methods=['POST'])
def leave_room(roomcode):
    room = get_or_create_room(roomcode)
    room.remove_player(session['uid'])
    return redirect(url_for('index'))

# @app.route('/login', methods=['GET'])
# def login():
#     return render_template('login.html')


# @app.route('/login', methods=['POST'])
# def login_post():
#     complaints = []
#     username = request.form['user_input'].strip()

#     username_taken = False
#     if newname in names.values():
#         if newname == names.get(session['uid'], None):
#             '''then it's your name, and it's okay'''
#         elif time() - name_last_used.get(newname, 0) > NAME_TIMEOUT:
#             '''then it's timed out, and it's okay'''
#         else:
#             username_taken = True

#     for condition, message in (
#             (username_taken, 'Username is already taken.'),
#             (not (set(newname) < set(ascii_letters + " ")), 'No special characters.'),
#             (len(newname) < 2, 'Username is too short'),
#             (len(newname) > 40, 'Username is too long')):

#         if condition:
#             complaints.append(message)

#     # Passed sanity checks
#     if len(complaints) <= 0:
#         session['username'] = username
#         return redirect(url_for('index'))

#     return render_template('login.html', complaints=complaints)


if __name__ == '__main__':
    app.run(debug=True)
