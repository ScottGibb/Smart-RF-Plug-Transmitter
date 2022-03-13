# Converting Old RF Plugs to Smart Plugs with Node-RED and Docker

# Summary
This project contains a system in which regular RF plugs can be used alongside smart plugs. This allows users to reuse
their old RF plugs as new smart plugs. Preventing e-waste and saving money. To do this, the following systems are needed:
- Smart Home Agent (Alexa, Google Home)
- [Node-RED](https://nodered.org/)
- Raspberry Pi

# Architecture
The system works using a Raspberry Pi as the central control system, which is running both Node-RED and the 
SocketTransmitter python script. These are running in their own docker container to allow for better modularisation.

![System Architecture](docs/System Diagram.png)

The Alexa devices are connected over the network using any IP link. Everything should work as long as the devices are on 
the same network as the Raspberry Pi running Node-RED.

- The Raspberry Pi is then connected to the 433MHz Transmitter module via the 5V, GND and Transmit pins.
- The flows attached to this repo are then used to communicate with the SocketTransmitter via TCP. This then sends the 
- required bitstream signal to the script running inside Docker. Which then turns the plugs on and off through the 
- 433MHz Transmitter.
- The system is built such that when the SocketTransmitter container is up and running, it never needs to be taken down.

# Node-RED Flows
The general flow used for Node-RED is shown below:

![Node Red Flow](docs/Node Red Flow.png)

Each Plug is set up as an Alexa-Home Node which then has two functions, turnOn and turnOff requests, which then feed into 
the function blocks triggering the TCP socket call to turn on and off the plugs.

# Parts
The parts required for the project are listed below:

- [Easy On Easy Off Plugs](https://www.amazon.co.uk/Home-Easy-Remote-Control-Socket/dp/B00KC7AHMM)

- [433MHz Transmitter Receiver Pack](https://www.aliexpress.com/item/4000018571977.html?spm=a2g0o.productlist.0.0.76831160l0sedh&algo_pvid=4ed97a32-f054-4d1c-8f60-14a1a476c9e2&algo_exp_id=4ed97a32-f054-4d1c-8f60-14a1a476c9e2-1&pdp_ext_f=%7B%22sku_id%22%3A%2210000000043504110%22%7D&pdp_pi=-1%3B0.61%3B-1%3B-1%40salePrice%3BGBP%3Bsearch-mainSearch)

- [Raspberry Pi Foundation](https://www.raspberrypi.org/)

- [Logic Analyser](https://www.amazon.co.uk/gp/product/B00DAYAREW/ref=ppx_yo_dt_b_search_asin_image?ie=UTF8&psc=1)

# Software Requirements

For the project to work, the following software is needed:

- [Node-RED](https://nodered.org/)
- [node-red-contrib-alexa-home-skill](https://flows.nodered.org/node/node-red-contrib-alexa-home-skill)
- [Portainer](https://www.portainer.io/)
- [Docker](https://www.docker.com/)

# Inspirations
The following projects inspired this project:
- [RF 433 MHZ (Raspberry Pi)
](https://www.instructables.com/RF-433-MHZ-Raspberry-Pi/)