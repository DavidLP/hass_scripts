import logging
import asyncio
import tempfile
from hbmqtt import client
from hbmqtt.mqtt.constants import QOS_0
from gtts import gTTS

logger = logging.getLogger(__name__)

# Time to talk to the speaker to prevent shutdown
ALIVE_TIME = 300  # in seconds
# Used console command to play mp3 file
MP3_CMD = 'mpg123 -q'
# MQTT settings
MQTT_SERVER = 'mqtts://pfuideibel.dnshome.de:8883'
MQTT_TOPIC = 'devices/#'
MQTT_CA = '/home/ha/mosquitto_certs/ca.crt'
MQTT_CRT = '/home/ha/mosquitto_certs/rpi2.crt'
MQTT_KEY = '/home/ha/mosquitto_certs/rpi2.key'


async def run_command_shell(command):
    """Run command in subprocess (shell)
    
    Note:
        This can be used if you wish to execute e.g. "copy"
        on Windows, which can only be executed in the shell.
    """
    # Create subprocess
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE)

    # Status
    # print('Started:', command, '(pid = ' + str(process.pid) + ')')

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    # Progress
    #if process.returncode == 0:
    #    print('Done:', command, '(pid = ' + str(process.pid) + ')')
    #else:
    #    print('Failed:', command, '(pid = ' + str(process.pid) + ')')

    # Result
    result = stdout.decode().strip()

    # Return stdout
    return result


async def output_google(text, lang):
    tts = gTTS(text=text, lang=lang)
    f = tempfile.NamedTemporaryFile(suffix='.mp3', delete=True)
    tts.save(f.name)
    await asyncio.sleep(3)
    logging.info('Google TTS (%s): %s', lang, text)
    await run_command_shell(MP3_CMD + ' ' + f.name)
    f.close()


async def output(text, lang):
    logger.info('Speak %s', text)
    if not 'On' in await monitor_status():
      await run_command_shell('export DISPLAY=:0; xset dpms force on')
      await asyncio.sleep(5)
    try:
        await output_google(text, lang)
    except IOError:  # Fallback if no internet connection
        await run_command_shell('espeak' + ' "' + text + '"')

async def test_pub():
    while True:
        logging.info('TESZ PUB')
        asyncio.ensure_future(c.publish('a/b', b'TEST MESSAGE WITH QOS_0'))
        await asyncio.sleep(2)

async def monitor_status():
    r = await run_command_shell('export DISPLAY=:0; xset q')
    return str(r[-8:])

async def check_monitor_status():
    status = None
    while True:
        stat_s = await monitor_status()
        logging.info(stat_s)
        if 'On' in stat_s:
            logging.info('MONITOR IS ON')
            if not status:
                asyncio.ensure_future(c.publish('devices/monitor/status', b'ON'))
                status = True
        elif 'Off' in stat_s:
            logging.info('MONITOR IS OFF')
            if status or status is None:
                asyncio.ensure_future(c.publish('devices/monitor/status', b'OFF'))
                status = False 
        await asyncio.sleep(2)  # Poll every 2 seconds

async def keep_alive():
    ''' Send empty sounds to prevent speaker power down '''
    while True:
        logger.info('Poll speaker to prevent power down')
        if q.empty():
            await q.put(('/devices/tts/say', b''))
        await asyncio.sleep(ALIVE_TIME)


async def consumer():
    while True:
        topic, text = await q.get()
        text = text.decode('ascii')
        if 'tts' in topic:
            if 'say' in topic:
                await output(text, lang='en')
            elif 'sag' in topic:
                await output(text, lang='de')
        if 'monitor' in topic:
            if 'status' not in topic:
                if 'ON' in text:
                    await run_command_shell('export DISPLAY=:0; xset dpms force on')
                else:
                    await run_command_shell('export DISPLAY=:0; xset dpms force off')

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
# FIXME: never called
#     await c.unsubscribe([MQTT_TOPIC])
#     logger.info("UnSubscribed")
#     await c.disconnect()


async def main():
    config = {
        'certfile': MQTT_CRT,
        'keyfile': MQTT_KEY,
        'keep_alive': 60,  # otherwise time out and broker disconnect
        'ping_delay': 1,
        'auto_reconnect': True,
        'reconnect_max_interval': 10,
        'reconnect_retries': 100
    }
    global c
    c = client.MQTTClient(config=config)
    global q
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    # loop.create_task(keep_alive())
    loop.create_task(consumer())
    loop.create_task(check_monitor_status())
    # loop.create_task(test_pub())
    loop.create_task(mqtt_rcv())

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
