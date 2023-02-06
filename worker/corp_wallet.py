from oauth import register_esi
from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from models import Character, CorpWalletEntry
from sqlalchemy.dialects.postgresql import insert
from dateutil import parser

async def handle_page(sess, esi, cur_page, char, division):
    for j in cur_page:
        entry = CorpWalletEntry(
            id = j["id"],
            amount = j["amount"],
            balance = j["balance"],
            context_id = j.get('context_id', -1),
            context_id_type = j.get('context_id_type', -1),
            date = dateparser.parse(j.get('date')),
            description = j['description'],
            first_party_id = j['first_party_id'],
            reason = j['reason'],
            ref_type = j['ref_type'],
            second_party_id = j['second_party_id'],
            division = division,
            source = char
        )
        try:
            sess.add(entry)
            session.commit()
        except Exception as e:
            pass

def corp_wallet_worker(cfg, division, char):
    async def worker():
        engine = create_engine(cfg['database']['uri'])
        with Session(engine, future=True) as sess:
            character = sess.execute(
                select(Character).filter_by(id=char)
            ).scalars().first()
            token = character.to_token()
            esi = AsyncOAuth2Client(
                client_id=cfg['esi']['client_id'],
                client_secret=cfg['esi']['client_secret'],
                authorize_url=cfg['esi']['authorize_url'],
                access_token_url=cfg['esi']['access_token_url'],
                refresh_token_url=cfg['esi']['access_token_url'],
                token_endpoint=cfg['esi']['access_token_url'],
                base_url=cfg['esi']['base_url'],
                token=token
            )
            verify = await esi.get('https://login.eveonline.com/oauth/verify')
            char_id = verify['CharacterID']
            affiliations = await esi.post('/characters/affiliations', json={'characters' : [char_id]})
            corp_id = affiliations[0]['corporation_id']
            res = await esi.get('/corporations/{}/wallets/{}/journal'.format(corp_id, division))
            pages = res.headers.get('X-Pages', 1)
            cur_page = res.json()

            await handle_page(sess, esi, cur_page, char, division)
            for page in range(2, int(pages)+1):
                res = await esi.get('/corporations/{}/wallets/{}/journal'.format(corp_id, division), params={'page': page})
                cur_page = res.json()
                await handle_page(sess, esi, cur_page, char, division)
            await esi.close()

    return worker