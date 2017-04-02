''' Entry point to start all scripts '''

import logging
import asyncio

from hass_scripts import tts

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    loop = asyncio.get_event_loop()
    loop.create_task(tts.main())
    loop.run_forever()

if __name__ == '__main__':
    main()
