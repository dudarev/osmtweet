def get_current_user(obj):
    url = obj.request.url
    if ('appspot' in url) or ('osmdonetsk' in url):
        from twitter_oauth_handler import OAuthClient,OAuthHandler
        client = OAuthClient('twitter', obj)
        if not client.get_cookie():
            user = None
        else:
            info = client.get('/account/verify_credentials')
            if info:
                user = info['screen_name']
            else:
                user = None
    else:
        from google.appengine.api import users as google_users
        user = google_users.get_current_user()
    return user

def create_login_url(obj,dest_url):
    url = obj.request.url
    if ('appspot' in url) or ('osmdonetsk' in url):
        login_url = "/oauth/twitter/login"
    else:
        from google.appengine.api import users as google_users
        login_url = google_users.create_login_url(dest_url)
    return login_url

def create_logout_url(obj,dest_url):
    url = obj.request.url
    if ('appspot' in url) or ('osmdonetsk' in url):
        logout_url = "/oauth/twitter/logout"
    else:
        from google.appengine.api import users as google_users
        logout_url = google_users.create_logout_url(dest_url)
    return logout_url 
