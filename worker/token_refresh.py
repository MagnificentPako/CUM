from oauth import register_esi
from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from models import Character, CorpWalletEntry
from sqlalchemy.dialects.postgresql import insert
from dateutil import parser
import httpx
from datetime import datetime, timedelta
import logging

def token_refresh_worker(cfg):
    async def worker():
        engine = create_engine(cfg['database']['uri'])
        with Session(engine, future=True) as sess:
            characters = sess.query(Character).all()
            for c in characters:
                logging.info('Refreshing token for character "{}"'.format(c.id))
                async with httpx.AsyncClient() as client:
                    auth = (cfg['esi']['client_id'], cfg['esi']['client_secret'])
                    payload = {
                        'grant_type': 'refresh_token',
                        'refresh_token': c.refresh_token,
                        'scope': ' '.join(cfg['esi']['scopes'])
                    }
                    res = await client.post(cfg['esi']['access_token_url'], auth=auth, data=payload)
                    new_token = res.json()
                    c.access_token = new_token['access_token']
                    c.refresh_token = new_token['refresh_token']
                    c.expires_at = (datetime.utcnow() + timedelta(seconds=new_token.get('expires_in', 0))).timestamp()
                    sess.commit()


    return worker