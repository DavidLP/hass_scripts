import asyncio
import os
import tempfile

from gtts import gTTS
import paho.mqtt.client as mqtt


# Used console command to play mp3 file
MP3_CMD = 'mpg123 -q'
MQTT_IP = '192.168.1.200'
MQTT_PORT = 8883
MQTT_CA = '/home/davidlp/git/hass_scripts/ca.crt'
MQTT_CRT = '/home/davidlp/git/hass_scripts/test.crt'
MQTT_KEY = '/home/davidlp/git/hass_scripts/test.key'


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/devices/tts/#")


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


def on_message(client, userdata, msg):
    ''' Called when mqtt message tts topic is received '''

    text = msg.payload.decode('ascii')
    q.put(text)
    if 'say' in msg.topic:
        output(text, lang='en')
    elif 'sag' in msg.topic:
        output(text, lang='de')
#     yield from q.put(text)

async def consumer():
    while True:
        value = await q.get()
        print('Consumed', value)

async def mqtt_rcv():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.tls_set(MQTT_CA, MQTT_CRT, MQTT_KEY)

    client.connect(MQTT_IP, MQTT_PORT, 60)
    client.loop_forever()


if __name__ == '__main__':
    #     client = mqtt.Client()
    q = asyncio.Queue()
    loop = asyncio.get_event_loop()
    loop.create_task(mqtt_rcv())
    loop.create_task(consumer())
    loop.run_forever()
#     print('DONE')
#     client.on_connect = on_connect
#     client.on_message = on_message
#
#     client.tls_set(MQTT_CA, MQTT_CRT, MQTT_KEY)
#
#     client.connect(MQTT_IP, MQTT_PORT, 60)
#
#
#
#     client.loop_forever()
