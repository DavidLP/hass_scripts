import logging
import asyncio
import os
import tempfile

from hbmqtt import client
from hbmqtt.mqtt.constants import QOS_0
from gtts import gTTS

logger = logging.getLogger(__name__)

# Used console command to play mp3 file
MP3_CMD = 'mpg123 -q'
MQTT_SERVER = 'mqtts://192.168.1.200:8883'
MQTT_TOPIC = '/devices/tts/#'
MQTT_CA = '/home/davidlp/git/hass_scripts/ca.crt'
MQTT_CRT = '/home/davidlp/git/hass_scripts/test.crt'
MQTT_KEY = '/home/davidlp/git/hass_scripts/test.key'


def output_google(text, lang):
    tts = gTTS(text=text, lang=lang)
    f = tempfile.NamedTemporaryFile(suffix='.mp3')
    tts.save(f.name)
    os.system(MP3_CMD + ' ' + f.name)
    f.close()


def output(text, lang):
    try:
        output_google(text, lang)
    except:  # Fallback if no internet connection
        os.system('espeak' + ' "' + text + '"')


async def consumer():
    while True:
        topic, text = await q.get()
        text = text.decode('ascii')
        if 'say' in topic:
            output(text, lang='en')
        elif 'sag' in topic:
            output(text, lang='de')


async def mqtt_rcv():
    await c.connect(MQTT_SERVER, cafile=MQTT_CA)
    await c.subscribe([
        (MQTT_TOPIC, QOS_0)
    ])
    logger.info("Subscribed")
    while True:
        message = await c.deliver_message()
        packet = message.publish_packet
        await q.put((packet.variable_header.topic_name, packet.payload.data))
        print("%s => %s" %
              (packet.variable_header.topic_name, str(packet.payload.data)))
# FIXME: never called
#     await c.unsubscribe([MQTT_TOPIC])
#     logger.info("UnSubscribed")
#     await c.disconnect()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    config = {
        'certfile': MQTT_CRT,
        'keyfile': MQTT_KEY
    }
    c = client.MQTTClient(config=config)
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    loop.create_task(consumer())
    loop.run_until_complete(mqtt_rcv())
