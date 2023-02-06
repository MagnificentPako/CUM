import asyncio
import toml
import uvicorn
from web.app import make_app
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.combining import OrTrigger
from worker import station_worker, region_worker, corp_wallet_worker, token_refresh_worker
from datetime import datetime
from log import logger, setup_logging

def load_config():
    return toml.load('config.toml')

async def start_workers(config):
    scheduler = AsyncIOScheduler()
    if(not 'cum' in config):
        return
    for name, worker in config['cum'].items():
        logger.info('Adding job {} ({}) to scheduler with {} minute interval.'.format(name, worker['type'], worker['minutes']))
        if(worker['type'] == 'station'):
            trigger = IntervalTrigger(minutes = worker['minutes'])
            scheduler.add_job( station_worker(config, worker['station_id'], worker['character'])
                             , OrTrigger([trigger, DateTrigger(datetime.now())]))
        if(worker['type'] == 'region'):
            trigger = IntervalTrigger(minutes = worker['minutes'])
            scheduler.add_job( region_worker(config, worker['region_id'], worker['character'])
                             , OrTrigger([trigger, DateTrigger(datetime.now())]))
        if(worker['type'] == 'corp_wallet'):
            trigger = IntervalTrigger(minutes = worker['minutes'])
            scheduler.add_job( corp_wallet_worker(config, worker['division'], worker['character'], name)
                             , OrTrigger([trigger, DateTrigger(datetime.now())]))
        if(worker['type'] == 'refresh'):
            trigger = IntervalTrigger(minutes = worker['minutes'])
            scheduler.add_job( token_refresh_worker(config)
                             , OrTrigger([trigger, DateTrigger(datetime.now())]))

    scheduler.start()

async def main():
    config = load_config()
    uvicorn_config = uvicorn.Config(make_app(config), host=config['web']['host'], port=config['web']['port'], proxy_headers=True)
    server = uvicorn.Server(uvicorn_config)
    setup_logging()
    await asyncio.gather(
        server.serve(),
        start_workers(config)
    )
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())