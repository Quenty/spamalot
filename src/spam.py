from flask import Flask, request, render_template, redirect, url_for, session
from random import choice, shuffle, randint
from string import ascii_letters
from time import time
import os
import app_static_routing
from models.Room import Room
from models.Configuration import MakeDefaultConfiguration, MakeConfiguration

WORDS = tuple(n.strip() for n in open(os.path.join(os.path.dirname(__file__), '../data/room_names.txt')))
NAME_TIMEOUT = 300  # in seconds

# ---- helpers ----


def new_room_code():
    for _ in range(50):
        tentative = choice(WORDS)
        if rooms.get(tentative) is None:
            return tentative
    return "BEANS"


def get_secret():
    if 'secret.txt' not in os.listdir('../'):
        open('../secret.txt', 'w').write(random_string(100))
    return open('../secret.txt').read()


def random_string(length):
    return ''.join(choice(ascii_letters) for _ in range(length))


# --- database ---
names = {}
name_last_used = {}
rooms = {}


def get_user_name_from_uid(uid):
    assert(uid)

    return names.get(uid, "[Internal Error: Unknown User]")

# --- framework ---


class ComplaintException(Exception):
    pass


app = Flask(__name__)
app.secret_key = get_secret()
app_static_routing.init_routes(app)


class Carafe:
    def __init__(self):
        self.name = self.__class__.__name__.lower()
        self.path = (f'/{self.name}/', '/')[self.name == 'index']
        self.template = f'{self.name}.html'

        app.add_url_rule(self.path, self.name, self._render, methods=['GET'])
        app.add_url_rule(self.path, self.name+'_p',
                         self.form, methods=['POST'])

        self.complaints = []

    def __init_subclass__(cls, **kwargs):
        cls()  # beaned lmao

    def _render(self):
        if 'uid' not in session:
            session['uid'] = random_string(50)

        if (session['uid'] not in names) and (self.name != 'login'):
            return redirect(url_for('login'))

        if session['uid'] in names:
            name_last_used[names[session['uid']]] = time()

        return self.render()

    def render(self):
        return render_template(self.template, **self._context())

    def form(self):
        try:
            self.complaints = []
            return self.process(request.form)
        except ComplaintException:
            return self.render()

    def complain(self, args):
        if type(args) is str:
            args = (args,)

        if args:
            self.complaints = args[:]
            raise ComplaintException()

    def _context(self):
        return {**(self.context() or {}),
                'complaints': self.complaints,
                'username': names.get(session['uid'], ''),
                'roomcode': session.get('room', '')}

    def context(self):
        return None

    process = NotImplemented

# --------- the pages themselves ----------


class Index(Carafe):
    pass


class Login(Carafe):
    def process(self, form):
        newname = form['user_input'].strip()

        username_taken = False
        if newname in names.values():
            if newname == names.get(session['uid'], None):
                '''then it's your name, and it's okay'''
            elif time() - name_last_used.get(newname, 0) > NAME_TIMEOUT:
                '''then it's timed out, and it's okay'''
            else:
                username_taken = True

        self.complain([message for condition, message in (
            (username_taken, 'Username is already taken.'),
            (not (set(newname) < set(ascii_letters + " ")), 'No special characters.'),
            (len(newname) < 2, 'Username is too short'),
            (len(newname) > 30, 'Username is too long'))
            if condition])

        # out with the old
        if newname in names.values():
            names[newname] = None

        # in with the new
        name_last_used[newname] = time()
        names[session['uid']] = newname
        return redirect(url_for('index'))


class CreateRandomRoom(Carafe):
    def render(self):
        room_code = new_room_code()
        rooms[room_code] = Room(session['uid'], room_code)
        session['room'] = room_code
        return redirect(url_for('create'))


class Create(Carafe):
    def context(self):
        return session.get('config', MakeDefaultConfiguration())

    def process(self, form):
        config = MakeConfiguration(form)

        self.complain(config['complaints'])

        room = rooms[session['room']]
        if room:
            room.set_configure(config)
        else:
            self.complain('Room does not exist')

        return redirect(url_for('game'))


class Join(Carafe):
    def process(self, form):
        room_code = ''.join(c for c in form['user_input'] if c in ascii_letters).lower()
        room = rooms.get(session['room'])
        if room is None:
            self.complain('That room does not exist')

        if room.has_player(session['uid']):
            return

        ok = room.add_player(session['uid'])

        if not ok:
            self.complain('That room is already full')

        session['room'] = room_code

        # elif room.full and session['uid'] not in room.uids:
        #     return redirect(url_for('game'))
        #     # self.complain('That room is already full')

        return redirect(url_for('game'))


class Game(Carafe):
    def context(self):
        room = rooms.get(session['room'], None)
        if room is None:
            return {}

        return {
            'roomcode': room.get_room_code(),
            'doing_config': room.is_configuring() and get_user_name_from_uid(room.get_creator_uid()) or False,
            'is_creator': session['uid'] == room.get_creator_uid(),
            'players': room.get_player_names(get_user_name_from_uid),
            'roles': room.get_roles_data_for_rendering(),
            'status': f'{room.get_player_count()}/{room.get_max_player_count()}',
            'role_info': room.get_role_info(session['uid'], get_user_name_from_uid),
        }

    def process(self, form):  # rematch
        roomcode = session['room']
        oldRoom = rooms[roomcode]
        session['config'] = oldRoom.get_configure()

        rooms[roomcode] = Room(session['uid'])
        session['room'] = roomcode

        return redirect(url_for('create'))


# and run the darned thing
if __name__ == '__main__':
    app.run(debug=False)
