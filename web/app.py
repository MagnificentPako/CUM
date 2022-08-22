from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import RedirectResponse
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from starlette.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.character import Character
from oauth import register_esi
import secrets
import base64
import binascii
from starlette.responses import Response
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser, requires
)

verify_url = 'https://login.eveonline.com/oauth/verify'

templates = Jinja2Templates(directory='web/templates')

class BasicAuthBackend(AuthenticationBackend):
    def __init__(self, pw):
        self.password = pw

    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'basic':
                return
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationError('Invalid basic auth credentials')

        username, _, password = decoded.partition(":")
        if(username == 'admin' and password == self.password):
            return AuthCredentials(["authenticated"]), SimpleUser(username)
        raise AuthenticationError('Invalid basic auth credentials')

def mk_homepage(mapping):
    @requires('authenticated', redirect='login')
    async def homepage(request):
        return templates.TemplateResponse('index.html', {'request': request, 'chars': mapping})
    return homepage

def mk_login_start(ctx, auth):
    async def login_start(request):
        request.session['char'] = ctx
        esi = auth.create_client('ESI')
        redirect_uri = request.url_for('oauth_callback')
        print(redirect_uri)
        return await esi.authorize_redirect(request, redirect_uri)
    return login_start

def mk_oauth_callback(cfg, auth):
    async def oauth_callback(request):
        esi = auth.create_client('ESI')
        print(request.session)
        token = await esi.authorize_access_token(request)
        verify = await esi.get(verify_url, token=token)
        char = Character(
            id = request.session['char'],
            access_token = token['access_token'],
            refresh_token = token['refresh_token'],
            token_type = token['token_type'],
            expires_at = token['expires_at'],
            character_id = verify.json()['CharacterID']
        )
        engine = create_engine(cfg['database']['uri'])
        with Session(engine) as session:
            session.add(char)
            session.commit()
        return RedirectResponse(request.url_for('home'))
    return oauth_callback

async def login(request):
    if request.user.is_authenticated:
        return RedirectResponse(request.url_for('home'))
    return Response('', status_code=401, headers={'WWW-Authenticate': 'Basic'})

def make_app(config):
    oauth = OAuth()
    register_esi(oauth, config)

    char_mapping = {}
    for c in config['characters']:
        char_mapping[c] = secrets.token_urlsafe(8)

    routes = [
        Route('/', endpoint=mk_homepage(char_mapping), name='home'),
        Route('/oauth/callback', endpoint=mk_oauth_callback(config, oauth), name='oauth_callback'),
        Route('/login', endpoint=login, name='login')
    ]

    for k,v in char_mapping.items():
        routes.append(Route('/{}-{}'.format(k, v), mk_login_start(k, oauth)))

    middleware = [
        Middleware(SessionMiddleware, secret_key=config['web']['session_secret']),
        Middleware(AuthenticationMiddleware, backend=BasicAuthBackend(config['web']['password']))
    ]

    return Starlette(routes=routes, middleware=middleware)