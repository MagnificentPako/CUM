def register_esi(oauth, config):
    oauth.register(
        name = 'ESI',
        client_id = config['esi']['client_id'],
        client_secret = config['esi']['client_secret'],
        authorize_url = config['esi']['authorize_url'],
        access_token_url = config['esi']['access_token_url'],
        client_kwargs={'scope': ' '.join(config['esi']['scopes'])}
    )