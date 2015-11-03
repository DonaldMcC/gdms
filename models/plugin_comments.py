# coding: utf8
db.define_table('plugin_comments_post',
        Field('tablename',writable=False,readable=False),
        Field('record_id','integer',writable=False,readable=False),
        Field('body','text',requires=IS_NOT_EMPTY()),
        auth.signature)

def fullname(user_id):
    if user_id is None:
        return "Unknown"
    return "%(first_name)s %(last_name)s (id:%(id)s)" % db.auth_user(user_id)
