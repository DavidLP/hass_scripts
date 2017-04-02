===============================================
Introduction
===============================================

Suscribes to the mqtt topic /devices/say words to use google text to speech to say words.

Installation
============
Needs linux with mpg123 installed to play mp3 files.

Linux
-----
This installation has been tested with Raspian and Python 3.6.

1. Prequites:
   sudo apt-get install mpg123 libyaml-dev

2. Install:

.. code-block:: bash

   python setup.py develop
