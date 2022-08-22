from oauth import register_esi
from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from models import Character, ItemType, StationMarketIteration, StationMarketEntry
from sqlalchemy.dialects.postgresql import insert
from dateutil import parser

async def handle_page(sess, esi, cur_page, existing_types, iteration, char):
    current_types = set(map(lambda x: x['type_id'], cur_page))
    new_types = list(current_types - existing_types)
    if(len(new_types) > 0):
        res = await esi.post('/universe/names', json=new_types)
        new_types_res = res.json()
        for t in new_types_res:
            sess.execute(insert(ItemType).values(id=t['id'], category=t['category'], name=t['name']))
        sess.commit()
    for item in cur_page:
        sess.execute(insert(StationMarketEntry).values(
            duration = item['duration'],
            is_buy_order = item['is_buy_order'],
            issued = parser.parse(item['issued']),
            location_id = item['location_id'],
            min_volume = item['min_volume'],
            order_id = item['order_id'],
            price = item['price'],
            range = item['range'],
            type_id = item['type_id'],
            volume_remain = item['volume_remain'],
            volume_total = item['volume_total'],
            source_char = char,
            iteration = iteration
        ))
    sess.commit()

async def prime_market_iteration(sess, char):
    if len(sess.execute(select(StationMarketIteration).where(StationMarketIteration.source_char==char)).scalars().all()) > 0:
        return
    sess.execute(insert(StationMarketIteration).values(source_char=char, iteration=1))
    sess.commit()

def region_worker(cfg, region, char):
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
            await prime_market_iteration(sess, char)
            current_iteration = sess.execute(select(StationMarketIteration).where(StationMarketIteration.source_char==char)).scalars().first()
            new_iteration = current_iteration.iteration + 1
            sess.execute(update(StationMarketIteration).where(StationMarketIteration.source_char==char).values(iteration=new_iteration))
            existing_types = set(map(lambda x: x.id, sess.execute(select(ItemType)).scalars().all()))
            res = await esi.get('/markets/{}/orders'.format(region))
            pages = res.headers.get('X-Pages', 1)
            cur_page = res.json()
            await handle_page(sess, esi, cur_page, existing_types, new_iteration, char)
            for page in range(2, int(pages)+1):
                existing_types = set(map(lambda x: x.id, sess.execute(select(ItemType)).scalars().all()))
                res = await esi.get('/markets/{}/orders'.format(region), params={'page': page})
                cur_page = res.json()
                await handle_page(sess, esi, cur_page, existing_types, new_iteration, char)
            await esi.aclose()
    return worker