from social_core.storage import UserMixin, BaseStorage, NonceMixin, AssociationMixin
from gluon.globals import current
import base64
import six

class User(object):
    """Social Auth user model"""
    def __init__(self, row):
        self.row = row
        self.id = row.id
        self.__dict__.update(self.row.as_dict())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            try:
                return self.id == other.id
            except AttributeError:
                pass
        return False

    def save(self):
        self.row.update(self.__dict__)
        self.row.update_record()

class W2PMixin(object):
    __tablename__ = None

    @classmethod
    def table(cls):
        return cls.db()[cls.__tablename__]

    @classmethod
    def db(cls):
        return current.plugin_social_auth.db

class UserSocialAuth(W2PMixin, UserMixin):
    """Social Auth association model"""
    __tablename__ = 'plugin_social_auth_user'

    def __init__(self, row):
        if row:
            self.row = row
            self.id = row.id
            self.provider = self.row.provider
            self.uid = self.row.oauth_uid
            self.extra_data = row.extra_data
            self.user = User(current.plugin_social_auth.auth.table_user()[self.row.oauth_user])

    def _save(self):
        if self.row:
            self.row.update_record()

    @classmethod
    def username_field(cls):
        return getattr(cls.user_model(), 'USERNAME_FIELD', 'username')

    @classmethod
    def get_username(cls, user):
        """Return the username for given user"""
        username_field = cls.username_field()
        return getattr(user, username_field,  None)

    @classmethod
    def username_max_length(cls):
        """Return the max length for username"""
        return current.plugin_social_auth.auth.table_user().username.length

    @classmethod
    def user_model(cls):
        """Return the user model"""
        return User

    @classmethod
    def changed(cls, user):
        """The given user instance is ready to be saved"""
        user.save()

    def set_extra_data(self, extra_data=None):
        if super(UserSocialAuth, self).set_extra_data(extra_data):
            self.row.extra_data = extra_data
            self._save()

    @classmethod
    def user_exists(cls, *args, **kwargs):
        """
        Return True/False if a User instance exists with the given arguments.
        Arguments are directly passed to filter() manager method.
        """
        if 'username' in kwargs:
            username = kwargs.pop('username')
            return None != cls.get_user(username)

    @classmethod
    def create_user(cls, *args, **kwargs):
        """Create a user with given username and (optional) email"""
        keys = {}
        for field in current.plugin_social_auth.plugin.SOCIAL_AUTH_USER_FIELDS:
            if field in kwargs:
                keys[field] = kwargs[field]

        row = current.plugin_social_auth.auth.get_or_create_user(keys)

        if row:
            return User(row)

    @classmethod
    def get_user(cls, pk):
        """Return user instance for given id"""
        row = cls.db()(current.plugin_social_auth.auth.table_user().username == pk).select().first()
        if row:
            return User(row)

    @classmethod
    def allowed_to_disconnect(cls, user, backend_name, association_id=None):
        """Return if it's safe to disconnect the social account for the
        given user"""
        table = cls.table()
        if association_id is not None:
            q = table.id != association_id
        else:
            q = table.provider != backend_name
        q &= (table.oauth_user == user.id)

        return not cls.db()(q).isempty()

    @classmethod
    def disconnect(cls, entry, on_disconnected=lambda x: None):
        """Disconnect the social account for the given user"""
        entry.row.delete_record()

        on_disconnected(entry.provider)

    @classmethod
    def get_social_auth(cls, provider, uid):
        """Return UserSocialAuth for given provider and uid"""
        if not isinstance(uid, six.string_types):
            uid = str(uid)
        db = cls.db()
        table = cls.table()
        row = db((table.provider == provider) &
                (table.oauth_uid == uid)).select().first()
        if row:
            return cls(row)

    @classmethod
    def get_social_auth_for_user(cls, user=None, provider=None, association_id=None):
        """Return all the UserSocialAuth instances for given user"""
        table = cls.table()

        # Build dynamic query based on kwargs
        filters = []
        for k, v in dict(id=association_id,
                         provider=provider,
                         oauth_user=user.id if user else None).iteritems():
            if None != v:
                filters.append(getattr(table, k) == v)
        query = reduce(lambda a, b: (a & b), filters)

        rows = cls.db()(query).select()

        if rows:
            return [cls(row) for row in rows]

    @classmethod
    def create_social_auth(cls, user, uid, provider):
        """Create a UserSocialAuth instance for given user"""
        if not isinstance(uid, six.string_types):
            uid = str(uid)
        user_id = cls.table().insert(oauth_user=user.id, oauth_uid=uid, provider=provider)
        if user_id:
            return cls(cls.table()[user_id])

class Nonce(W2PMixin, NonceMixin):
    """One use numbers"""
    __tablename__ = 'plugin_social_auth_nonce'

    def __init__(self, row):
        self.row = row
        self.id = row.id
        self.server_url = row.server_url
        self.timestamp = row.nonce_timestamp
        self.salt = row.salt

    @classmethod
    def use(cls, server_url, timestamp, salt):
        """Create a Nonce instance"""
        db = cls.db()
        table = cls.table()
        row = db((table.server_url == server_url) &
                (table.nonce_timestamp == timestamp) &
                (table.salt == salt)).select().first()
        if row:
            return cls(row)
        else:
            nonce_id = table.insert(server_url=server_url, nonce_timestamp=timestamp, salt=salt)
            if nonce_id:
                return cls(cls.table()[nonce_id])

class Association(W2PMixin, AssociationMixin):
    """OpenId account association"""
    __tablename__ = 'plugin_social_auth_association'

    def __init__(self, row):
        self.row = row
        self.id = row.id
        self.handle = row.handle
        self.secret = row.secret
        self.issued = row.issued
        self.lifetime = row.lifetime
        self.assoc_type = row.assoc_type

    @classmethod
    def store(cls, server_url, association):
        """Create an Association instance"""
        table = cls.table()
        row = cls.db()((table.server_url == server_url) &
                       (table.handle == association.handle)).select().first()
        if not row:
            table.insert(server_url=server_url,
                         handle=association.handle,
                         secret=base64.encodestring(association.secret),
                         issued=association.issued,
                         lifetime=association.lifetime,
                         assoc_type=association.assoc_type)

    @classmethod
    def get(cls, *args, **kwargs):
        """Get an Association instance"""
        table = cls.table()

        # Build dynamic query based on kwargs
        filters = []
        for k, v in kwargs.iteritems():
            filters.append(getattr(table, k) == v)
        query = reduce(lambda a, b: (a & b), filters)

        rows = cls.db()(query).select()
        return [cls(row) for row in rows]

    @classmethod
    def remove(cls, ids_to_delete):
        """Remove an Association instance"""
        cls.db()(cls.table().id.belongs(ids_to_delete)).delete()

class W2PStorage(BaseStorage):
    user = UserSocialAuth
    nonce = Nonce
    association = Association