import asyncio
import toml
import uvicorn
from web.app import make_app
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.combining import OrTrigger
from worker import station_worker, region_worker
from datetime import datetime
from log import logger, setup_logging

def load_config():
    return toml.load('config.toml')

async def start_workers(config):
    scheduler = AsyncIOScheduler()
    for name, worker in config['cum'].items():
        if(worker['type'] == 'station'):
            logger.info('Adding job {} ({}) to scheduler with {} minute interval.'.format(name, worker['type'], worker['minutes']))
            trigger = IntervalTrigger(minutes = worker['minutes'])
            scheduler.add_job( station_worker(config, worker['station_id'], worker['character'])
                             , OrTrigger([trigger, DateTrigger(datetime.now())]))
        if(worker['type'] == 'region'):
            logger.info('Adding job {} ({}) to scheduler with {} minute interval.'.format(name, worker['type'], worker['minutes']))
            trigger = IntervalTrigger(minutes = worker['minutes'])
            scheduler.add_job( region_worker(config, worker['region_id'], worker['character'])
                             , OrTrigger([trigger, DateTrigger(datetime.now())]))
    scheduler.start()

async def main():
    config = load_config()
    uvicorn_config = uvicorn.Config(make_app(config), host=config['web']['host'], port=config['web']['port'])
    server = uvicorn.Server(uvicorn_config)
    setup_logging()
    await asyncio.gather(
        server.serve(),
        start_workers(config)
    )
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())