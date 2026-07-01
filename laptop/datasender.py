import time
import ntcore

LISTENER_NAME = "laptop-listener"
TEAM_NUMBER = 1076
IS_SIMULATION = False

nt_instance = None
fms_table = None

match_time_sub = None
is_red_sub = None
auton_winner_sub = None

def init():
    global nt_instance, fms_table, match_time_sub, is_red_sub, auton_winner_sub
    nt_instance = ntcore.NetworkTableInstance.getDefault()

    if IS_SIMULATION:
        nt_instance.setServer("localhost")
    else:
        nt_instance.setServerTeam(TEAM_NUMBER)

    nt_instance.startClient4(LISTENER_NAME)


    time.sleep(5.0)

    if not nt_instance.isConnected():
        raise ConnectionRefusedError("Unable to connect to NT4 client")

    fms_table = nt_instance.getTable("FMSInfo")

    if IS_SIMULATION:
        match_time_sub = nt_instance.getTable("AdvantageKit").getSubTable("DriverStation").getDoubleTopic("MatchTime").subscribe(0.0)
    else:
        match_time_sub = fms_table.getDoubleTopic("MatchTime").subscribe(-1.0)
    is_red_sub = fms_table.getBooleanTopic("IsRedAlliance").subscribe(True)
    auton_winner_sub = fms_table.getStringTopic("GameSpecificMessage").subscribe("")

def getSendableMessage():
    if not nt_instance.isConnected():
        raise ConnectionError("NT4 client not connected")

    match_time = match_time_sub.get()
    is_red = is_red_sub.get()
    auton_winner = auton_winner_sub.get()
    
    return f"{int(match_time) if match_time >= 0 else 0:03d}{1 if is_red else 0}{1 if auton_winner=="R" else 0}"


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

            time.sleep(5.0) # Wait five seconds to try again
            continue
    else:
        try:
            print(getSendableMessage())
            time.sleep(0.5)
        except Exception as e:
            print(f"Runtime error occured: {e}. Will disconnect and attempt to reconnect.")
            nt_instance.stopClient()
            nt_instance = None
            time.sleep(1.0)