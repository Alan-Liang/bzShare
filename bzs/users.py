
import pickle
import random
import base64

from . import const
from . import db
from . import utils

class UserManagerType:
    class User:
        """A user that acts as a fundamental functional group in bzShare."""
        def __init__(self, handle=None, password=None, usergroups=None, usr_name=None, usr_description=None, master=None):
            self.master          = master # Parent
            # User handle, composed only of non-capital letters, numbers and underline,
            # While not exceeding the limit of 32-byte length
            self.handle          = handle or 'guest'
            # Password is defaultly set to blank.
            self.password        = password or ''
            # A group of usergroups that the user belongs to.
            self.usergroups      = usergroups or {'public'}
            # Cookies that are used to login.
            self.cookie          = None
            # IP Addresses that the user used to login.
            self.ip_addresses    = []
            # These are a set of user-defined options.
            self.usr_name        = usr_name or 'Guest'
            self.usr_description = usr_description or 'The guy who just wanders around.'
            self.usr_email       = ''
            # These are a great amount of social linkages.
            self.followers       = []
            self.friends         = []
            # Specify data indefinitely or load from pickle pls.
            return
        def save_data(self):
            bin_data = pickle.dumps(self)
            if not self.master.usr_db.execute("SELECT handle FROM users WHERE handle = %s;", (self.handle,)):
                self.master.usr_db.execute("INSERT INTO users (handle, data) VALUES (%s, %s);", (self.handle, bin_data))
            else:
                self.master.usr_db.execute("UPDATE users SET data = %s WHERE handle = %s;", (bin_data, self.handle))
            return
        def login(self):
            if not self.cookie:
                self.cookie = utils.get_new_cookie(self.master.users_cookies)
                self.master.users_cookies[self.cookie] = self.handle
                self.save_data()
            return self.cookie
        def logout(self):
            if self.cookie:
                del self.master.users_cookies[self.cookie]
                self.cookie = None
                self.save_data()
            return
        def add_ip_address(self, _ip):
            self.ip_addresses.append(_ip)
            self.ip_addresses = self.ip_addresses[:16]
            return
        pass

    def __init__(self, database=None):
        """Loads user content and configurations from database."""
        if not database:
            raise AttributeError('Must provide a database')
        self.users         = dict() # string -> User
        self.users_cookies = dict() # string -> string(handle)
        self.usergroups    = dict() # string -> string(name)
        self.usr_db        = database # Database
        # Selecting usergroups
        item = self.usr_db.execute("SELECT index, data FROM core WHERE index = 'usergroups';")
        try:
            item = pickle.loads(item[0][1])
            self.usergroups = item # Uploaded.
        except:
            item = set()
            self.add_usergroup('public', 'Public')
        # Done attribution, now selecting users
        for item in self.usr_db.execute("SELECT handle, data FROM users;"):
            handle, bin_data = item
            n_usr = pickle.loads(bin_data)
            # Injecting into index
            self.add_user(n_usr)
        # In case someone is missing... :)
        if 'guest' not in self.users:
            n_usr = self.User(master=self)
            self.add_user(n_usr)
            n_usr.save_data()
        # Adding superusers
        if 'kernel' not in self.users:
            n_usr = self.User(
                handle = 'kernel',
                password = const.get_const('server-admin-password'),
                usergroups = {'public'},
                usr_name = 'bzShare Kernel',
                usr_description = 'The core manager of bzShare.',
                master = self
            )
            self.add_user(n_usr)
            # This should never be inserted into server database.
        return

    def add_user(self, n_usr):
        self.users[n_usr.handle] = n_usr
        if n_usr.cookie:
            self.users_cookies[n_usr.cookie] = n_usr.handle
        return

    def add_usergroup(self, n_grp, grp_name):
        self.usergroups[n_grp] = grp_name
        usg_raw = pickle.dumps(self.usergroups)
        if not self.usr_db.execute("SELECT index FROM core WHERE index = %s;", ('usergroups',)):
            self.usr_db.execute("INSERT INTO core (index, data) VALUES (%s, %s)", ('usergroups', usg_raw))
        else:
            self.usr_db.execute("UPDATE core SET data = %s WHERE index = %s;", ('usg_raw', 'usergroups'))
        return

    def login_user(self, handle, password):
        usr = self.get_user_by_name(handle)
        if usr.handle == 'guest':
            return None
        if usr.password != password:
            return None
        return usr.login()

    def logout_user(self, handle):
        usr = self.get_user_by_name(handle)
        if usr.handle == 'guest':
            return
        return usr.logout()

    def get_user_by_name(self, name):
        if name in self.users:
            return self.users[name]
        if 'guest' in self.users:
            return self.users['guest']
        # Must gurantee a user
        return self.User(master=self)

    def get_user_by_cookie(self, cookie):
        if cookie in self.users_cookies:
            return self.get_user_by_name(self.users_cookies[cookie])
        # The one who do not require a cookie to login.
        return self.get_user_by_name('guest')

    def get_name_by_id(self, n_id):
        if n_id in self.usergroups:
            return self.usergroups[n_id]
        return get_user_by_name(n_id).usr_name

UserManager = UserManagerType(
    database = db.Database
)

################################################################################
# Exported functions

def add_user(user):
    return UserManager.add_user(user)

def add_usergroup(usergroup, usergroup_name):
    return UserManager.add_usergroup(usergroup, usergroup_name)

def login_user(handle, password):
    return UserManager.login_user(handle, password)

def logout_user(handle):
    return UserManager.logout_user(handle)

def get_user_by_name(name):
    return UserManager.get_user_by_name(name)

def get_user_by_cookie(cookie):
    return UserManager.get_user_by_cookie(cookie)

def get_name_by_id(n_id):
    return UserManager.get_name_by_id(n_id)
