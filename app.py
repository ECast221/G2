from sys import stdout
from imagerender import ImageDisplayer
import logging
from flask import Flask, render_template, Response, jsonify, redirect, session, url_for
from flask_socketio import SocketIO
from camera import Camera
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stdout))
socketio = SocketIO(app)
camera = Camera(ImageDisplayer())
oauth = OAuth(app)


google = oauth.register(
    name='google',
    client_id='114873956274-4llb40osg11j0hu5dk9h7mprnj65v80i.apps.googleusercontent.com',
    client_secret='eDGXKaqV0UvaMbBqVt--0EoJ',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/')
def loginPage():
    return render_template('login.html')


@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    return redirect('/home')


@socketio.on('input image', namespace='/test')
def test_message(input):
    input = input.split(",")[1]
    camera.enqueue_input(input)


@socketio.on('connect', namespace='/test')
def test_connect():
    app.logger.info("client connected")


@app.route('/streamingpage')
def stream():
    return render_template('stream.html')


def gen():
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/home')
def home():
    """Video streaming home page."""
    email = dict(session).get('email', None)
    return render_template('index.html')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


if __name__ == '__main__':
    socketio.run(app)
