## Building Instructions
The file contains the instructions for scanning your own plugs and adding them to the flow diagrams in Node-Red. 
As discussed in the README.md, the system uses Docker to containerise the critical subsystems.

## Scanning the Plug Frequency
If the developer has a different set of plugs than those specified in the ReadMe. The entire system can still work. 
It means extra work will be needed to ensure NodeRed can communicate with the Plugs

To scan the frequency that the plug uses, five bits of equipment are needed:
- Logic Analyser - Required for seeing the signals Transmitted by the Remote
- 433MHz Receiver - Required to receive the On, Off signals from the remote
- RF Plugs Remote - Required to send the On, Off Signals
- Some form of power source (Raspberry Pi, Bench Power Supply)
- Laptop- Required to View the Logic Analyser Signals

The diagram below describes visually how the monitoring system should be set up:
![Scanning System Diagram](docs/Scanning System Diagram.png)

Once this architecture is implemented, each button on the remote should be pressed one after another, and the waveform 
captured using the Signal Analyser software of your choice. Once captured, it should be converted into a BitString and 
kept in a file for future use in NodeRed. You should also capture the short and long delays so that the waveform can be 
accurately reproduced.

Once all this information is gathered, inside NodeRed, the function blocks will need changed to contain the correct 
bit sequences.

## Setting Up the RF Transmitter Docker Container
For setting up the Docker Container, the Dockerfile is used to first create the image, and then docker-compose is used to 
launch the container:

```console
 docker build -t rf_transmitter:v1 .
 docker-compose up -d
```
For more information regarding Docker and how to work with Dockerfiles, please consult the
[Docker Docs](https://docs.docker.com/).

## Integration with Node Red
In terms of Integrating with nodeRed, you have to make sure the system's IP address running the SocketTransmitter 
container is put into the NodeRed flow. Otherwise, it will never connect. The project used the same Raspberry Pi for 
both NodeRed and the SocketTransmitter.