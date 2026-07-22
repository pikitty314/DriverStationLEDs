import time
import ntcore
import serial

LISTENER_NAME = "laptop-listener"
TEAM_NUMBER = 1076
ROBOT_IP = "10.10.76.1"
IS_SIMULATION = False

PICO_PORT = "COM3"
PICO_BAUDRATE = 115200

nt_instance = None
fms_table = None
driverstation_subtable = None

match_time_sub = None
is_autonomous_sub = None
is_red_sub = None
auton_winner_sub = None

serial_instance = None

def init():
    global nt_instance, serial_instance, fms_table, driverstation_subtable, match_time_sub, is_autonomous_sub, is_red_sub, auton_winner_sub
    nt_instance = ntcore.NetworkTableInstance.getDefault()

    if IS_SIMULATION:
        nt_instance.setServer("localhost")
    else:
        nt_instance.setServerTeam(TEAM_NUMBER)
        # nt_instance.setServer(ROBOT_IP)

    nt_instance.startClient4(LISTENER_NAME)

    serial_instance = serial.Serial(port=PICO_PORT, baudrate=PICO_BAUDRATE, timeout=1)

    time.sleep(5.0)

    if not nt_instance.isConnected():
        raise ConnectionRefusedError("Unable to connect to NT4 client")
    
    if not serial_instance.is_open:
        raise ConnectionRefusedError(f"Unable to connect to Pi Pico on {PICO_PORT}")

    fms_table = nt_instance.getTable("FMSInfo")
    driverstation_subtable = nt_instance.getTable("AdvantageKit").getSubTable("DriverStation")

    match_time_sub = driverstation_subtable.getDoubleTopic("MatchTime").subscribe(-1.0)
    is_red_sub = fms_table.getBooleanTopic("IsRedAlliance").subscribe(True)
    is_autonomous_sub = driverstation_subtable.getBooleanTopic("Autonomous").subscribe(False)
    auton_winner_sub = fms_table.getStringTopic("GameSpecificMessage").subscribe("A")

def getSendableMessage():
    if not nt_instance.isConnected():
        raise ConnectionError("NT4 client not connected")

    match_time = match_time_sub.get()
    is_red = is_red_sub.get()
    is_autonomous = is_autonomous_sub.get()
    auton_winner = auton_winner_sub.get()

    if is_autonomous and int(match_time) > 0:
        match_time = match_time + 140
        auton_winner = "A"
    
    return f"{'R' if is_red else 'B'}{auton_winner if not is_autonomous else "A"}{int(match_time) if match_time >= 0 else 0:03d}"

def sendData(data):
    global serial_instance

    if not serial_instance.is_open:
        raise ConnectionError(f"Pi Pico on {PICO_PORT} not connected")
    
    serial_instance.write(f"{data}\n".encode("UTF-8"))
    
    

while True:
    if nt_instance is None:
        try:
            init()
            time.sleep(2.0)
        except Exception as e:
            print(f"Intitialization failed: {e}, trying again.")

            if nt_instance is not None:
                nt_instance.stopClient()
                nt_instance = None

            if serial_instance is not None:
                serial_instance.close()
                serial_instance = None

            time.sleep(5.0) # Wait five seconds to try again
            continue
    else:
        try:
            data = getSendableMessage()
            #print(data)
            sendData(data)
            time.sleep(0.5)
        except Exception as e:
            print(f"Runtime error occured: {e}. Will disconnect and attempt to reconnect.")
            nt_instance.stopClient()
            serial_instance.close()
            nt_instance = None
            serial_instance = None
            time.sleep(1.0)