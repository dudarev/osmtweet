from google.appengine.ext import db

class Changeset(db.Model):

    id = db.IntegerProperty()
    created_at = db.DateTimeProperty()
    user = db.StringProperty()
    comment = db.TextProperty()
    created_by = db.StringProperty()

    link_url = db.StringProperty(default=None)
    tweet = db.TextProperty(default=None)

    is_prepared = db.BooleanProperty(default=False)
    is_tweeted = db.BooleanProperty(default=False)
