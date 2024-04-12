from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.secret_key = 'gandi_is_daemury'

oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='여기 키 입력',
    consumer_secret='여기 비번키 입력',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        return f'Logged in as: {me.data["email"]}'
    return 'You are not logged in! <a href="/login">Login with Google</a>'


@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={}, error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    return f'Logged in as: {me.data["email"]}'


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


if __name__ == '__main__':
    app.run(debug=True)