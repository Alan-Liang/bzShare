
import base64
import mako
import mako.template
import math
import mimetypes
import random
import re
import time
import uuid

from . import const

################################################################################
# MIME Types

mime_types_dict = {}

def parse_mime_types():
    global mime_types_dict
    mime_types_dict = mimetypes.read_mime_types('./bzs/mime.types')
    if not mime_types_dict:
        mime_types_dict = {}
    return True

def guess_mime_type(filename):
    extension = re.findall(r'(.[^.]*)$', filename)
    extension = extension[0] if extension else '.'
    extension = mime_types_dict[extension] if extension in mime_types_dict else 'application/octet-stream'
    return extension

parse_mime_types()

################################################################################
# File data management

def get_static_data(filename):
    filename = re.sub('[?&].*$', '', filename)
    hfile = open(filename, 'rb')
    data = hfile.read()
    return data

def get_static_data_utf(filename):
    return get_static_data(filename).decode('utf-8', 'ignore')

def format_file_size(size_b, use_binary=False, verbose=False):
    if not use_binary:
        if not verbose:
            complexity_idx = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        else:
            complexity_idx = ['Bytes', 'Kilobytes', 'Megabytes', 'Gigabytes', 'Terabytes', 'Petabytes', 'Exabytes', 'Zettabytes', 'Yottabytes']
        try:
            complexity = int(math.log(size_b, 1000))
        except:
            complexity = 0
        size_f = size_b / 1000 ** complexity
        complexity_s = complexity_idx[complexity]
    else:
        if not verbose:
            complexity_idx = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
        else:
            complexity_idx = ['Bytes', 'Kibibytes', 'Mebibytes', 'Gibibytes', 'Tebibytes', 'Pebibytes', 'Exbibytes', 'Zebibytes', 'Yobibytes']
        try:
            complexity = int(math.log(size_b, 1000))
        except:
            complexity = 0
        size_f = size_b / 1024 ** complexity
        complexity_s = complexity_idx[complexity]
    return '%.2f %s' % (size_f, complexity_s)

def preprocess_webpage(data, content_user, **additional_arguments):
    if type(data) == bytes:
        data = data.decode('utf-8', 'ignore')
    data = mako.template.Template(
        text=data,
        input_encoding='utf-8',
        output_encoding='utf-8').render(
            placeholder_version_number = const.get_const('version'),
            placeholder_copyright_message = const.get_const('copyright'),
            user_is_administrator = 'Administrators' in content_user.usergroups,
            user_is_standard_user = 'Users' in content_user.usergroups,
            current_user_name = content_user.usr_name,
            current_user_description = content_user.usr_description,
            current_user_followers = len(content_user.followers),
            current_user_friends = len(content_user.friends),
            current_user_usergroups = content_user.usergroups,
            current_user_groups = len(content_user.usergroups),
            **additional_arguments
        )
    return data

################################################################################
# Time operations

def get_current_time():
    """Gets the current time, in float since epoch."""
    return float(time.time())

################################################################################
# UUID operations

def get_new_uuid(uuid_, uuid_list=None):
    """Creates a new UUID that is not in 'uuid_list' if given."""
    if not uuid_:
        uuid_ = uuid.uuid4()
        if type(uuid_list) in [set, dict]:
            while uuid_ in uuid_list:
                uuid_ = uuid.uuid4()
    return uuid_

def get_new_cookie(cookies_list=None):
    cookie = ''
    if not cookies_list:
        cookies_list = ['']
    while cookie in cookies_list or not cookie:
        cookie = base64.b64encode(str(random.randrange(0, 10**1024)).ljust(128)[:128].encode(
'utf-8', 'ignore')).decode('utf-8', 'ignore')
    return cookie
