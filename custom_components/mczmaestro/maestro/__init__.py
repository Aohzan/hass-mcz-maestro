"""MCZ Maestro."""
import websocket

import logging


_LOGGER = logging.getLogger(__name__)


class MaestroController:
    """Control the MCZ."""

    def __init__(self, host: str, port: int, timeout: int = 60) -> None:
        """Init the MCZ."""
        self._host = host
        self._port = str(port)
        self._server = websocket.create_connection(
            f"ws://{self._host}:{self._port}", timeout=timeout
        )

    @property
    def host(self) -> str:
        """Return the server host."""
        return self._host

    @property
    def port(self) -> str:
        """Return the server port."""
        return self._port

    @property
    def connected(self) -> bool:
        """Return true if connected to the ws server."""
        return self._server.connected

    def send(self, message) -> None:
        """Send a message."""
        self._server.send(message)

    def receive(self) -> dict:
        """Get data."""
        data = self._server.recv()
        return process_infostring(data)


class MaestroStoveState:
    """Maestro Stove State."""

    def __init__(self, stateid, description, onoroff):
        """Init a new state."""
        self.stateid = stateid  # Position in recuperoinfo-frame
        self.description = description  # Maestro command ID to be sent via websocket
        self.onoroff = onoroff  # Message type


class MaestroInformation:
    """Maestro Information. Consists of a readable name., a websocket ID and a command type."""

    def __init__(self, frameid, name, messagetype):
        """Init a new information."""
        self.frameid = frameid  # Position in recuperoinfo-frame
        self.name = name  # Maestro command ID to be sent via websocket
        self.messagetype = messagetype  # Message type


MAESTRO_STOVESTATE = [
    MaestroStoveState(0, "Off", 0),
    MaestroStoveState(1, "Checking hot or cold", 1),
    MaestroStoveState(2, "Cleaning cold", 1),
    MaestroStoveState(3, "Loading Pellets Cold", 1),
    MaestroStoveState(4, "Start 1 Cold", 1),
    MaestroStoveState(5, "Start 2 Cold", 1),
    MaestroStoveState(6, "Cleaning Hot", 1),
    MaestroStoveState(7, "Loading Pellets Hot", 1),
    MaestroStoveState(8, "Start 1 Hot", 1),
    MaestroStoveState(9, "Start 2 Hot", 1),
    MaestroStoveState(10, "Stabilising", 1),
    MaestroStoveState(11, "Power 1", 1),
    MaestroStoveState(12, "Power 2", 1),
    MaestroStoveState(13, "Power 3", 1),
    MaestroStoveState(14, "Power 4", 1),
    MaestroStoveState(15, "Power 5", 1),
    MaestroStoveState(30, "Diagnostics", 0),
    MaestroStoveState(31, "On", 1),
    MaestroStoveState(40, "Extinguish", 1),
    MaestroStoveState(41, "Cooling", 1),
    MaestroStoveState(42, "Cleaning Low", 1),
    MaestroStoveState(43, "Cleaning High", 1),
    MaestroStoveState(44, "UNLOCKING SCREW", 0),
    MaestroStoveState(45, "Auto Eco", 0),
    MaestroStoveState(46, "Standby", 0),
    MaestroStoveState(48, "Diagnostics", 0),
    MaestroStoveState(49, "Loading Auger", 0),
    MaestroStoveState(50, "Error A01 - Ignition failed", 0),
    MaestroStoveState(51, "Error A02 - No flame", 0),
    MaestroStoveState(52, "Error A03 - Tank overheating", 0),
    MaestroStoveState(53, "Error A04 - Flue gas temperature too high", 0),
    MaestroStoveState(54, "Error A05 - Duct obstruction - Wind", 0),
    MaestroStoveState(55, "Error A06 - Bad printing", 0),
    MaestroStoveState(56, "Error A09 - SMOKE PROBE", 0),
    MaestroStoveState(57, "Error A11 - GEAR MOTOR", 0),
    MaestroStoveState(58, "Error A13 - MOTHERBOARD TEMPERATURE", 0),
    MaestroStoveState(59, "Error A14 - DEFECT ACTIVE", 0),
    MaestroStoveState(60, "Error A18 - WATER TEMP ALARM", 0),
    MaestroStoveState(61, "Error A19 - FAULTY WATER PROBE", 0),
    MaestroStoveState(62, "Error A20 - FAILURE OF AUXILIARY PROBE", 0),
    MaestroStoveState(63, "Error A21 - PRESSURE SWITCH ALARM", 0),
    MaestroStoveState(64, "Error A22 - ROOM PROBE FAULT", 0),
    MaestroStoveState(65, "Error A23 - BRAZIL CLOSING FAULT", 0),
    MaestroStoveState(66, "Error A12 - MOTOR REDUCER CONTROLLER FAILURE", 0),
    MaestroStoveState(67, "Error A17 - ENDLESS SCREW JAM", 0),
    MaestroStoveState(69, "WAITING FOR SECURITY ALARMS", 0),
]

MAESTRO_MESSAGE_TYPE_TEMP = "temperature"
MAESTRO_MESSAGE_TYPE_INT = "int"
MAESTRO_MESSAGE_TYPE_3WAY = "3way"
MAESTRO_MESSAGE_TYPE_BRAZIER = "brazier"
MAESTRO_MESSAGE_TYPE_TIMESPAN = "timespan"
MAESTRO_MESSAGE_TYPE_ONOFF = "onoff"

MAESTRO_INFORMATION = [
    MaestroInformation(0, "Messagetype", "MaestoMessageType"),
    MaestroInformation(1, "Stove_State", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(2, "Fan_State", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(3, "DuctedFan1", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(4, "DuctedFan2", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(5, "Fume_Temperature", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(6, "Ambient_Temperature", MAESTRO_MESSAGE_TYPE_TEMP),
    MaestroInformation(7, "Puffer_Temperature", MAESTRO_MESSAGE_TYPE_TEMP),
    MaestroInformation(8, "Boiler_Temperature", MAESTRO_MESSAGE_TYPE_TEMP),
    MaestroInformation(9, "NTC3_Temperature", MAESTRO_MESSAGE_TYPE_TEMP),
    MaestroInformation(10, "Candle_Condition", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(11, "ACTIVE_Set", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(12, "RPM_Fam_Fume", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(13, "RPM_WormWheel_Set", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(14, "RPM_WormWheel_Live", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(15, "3WayValve", MAESTRO_MESSAGE_TYPE_3WAY),
    MaestroInformation(16, "Pump_PWM", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(17, "Brazier", MAESTRO_MESSAGE_TYPE_BRAZIER),
    MaestroInformation(
        18, "Profile", MAESTRO_MESSAGE_TYPE_INT
    ),  # 0, 10 = Manual, 1 & 11 = Dynamic, Overnight, Comfort, Power
    MaestroInformation(19, "Modbus_Address", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(20, "Active_Mode", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(21, "Active_Live", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(22, "Control_Mode", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(23, "Eco_Mode", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(24, "Silent_Mode", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(25, "Chronostat", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(26, "Temperature_Setpoint", MAESTRO_MESSAGE_TYPE_TEMP),
    MaestroInformation(27, "Boiler_Setpoint", MAESTRO_MESSAGE_TYPE_TEMP),
    MaestroInformation(28, "Temperature_Motherboard", MAESTRO_MESSAGE_TYPE_TEMP),
    MaestroInformation(29, "Power_Level", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(30, "FirmwareVersion", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(31, "DatabaseID", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(32, "Date_Time_Hours", MAESTRO_MESSAGE_TYPE_INT),  # time (0-23)
    MaestroInformation(33, "Date_Time_Minutes", MAESTRO_MESSAGE_TYPE_INT),  # (0-29)
    MaestroInformation(34, "Date_Day_Of_Month", MAESTRO_MESSAGE_TYPE_INT),  # (1-31)
    MaestroInformation(35, "Date_Month", MAESTRO_MESSAGE_TYPE_INT),  # (1-12)
    MaestroInformation(36, "Date_Year", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(37, "Total_Operating_Hours", MAESTRO_MESSAGE_TYPE_TIMESPAN),
    MaestroInformation(
        38, "Hours_Of_Operation_In_Power1", MAESTRO_MESSAGE_TYPE_TIMESPAN
    ),
    MaestroInformation(
        39, "Hours_Of_Operation_In_Power2", MAESTRO_MESSAGE_TYPE_TIMESPAN
    ),
    MaestroInformation(
        40, "Hours_Of_Operation_In_Power3", MAESTRO_MESSAGE_TYPE_TIMESPAN
    ),
    MaestroInformation(
        41, "Hours_Of_Operation_In_Power4", MAESTRO_MESSAGE_TYPE_TIMESPAN
    ),
    MaestroInformation(
        42, "Hours_Of_Operation_In_Power5", MAESTRO_MESSAGE_TYPE_TIMESPAN
    ),
    MaestroInformation(43, "Hours_To_Service", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(44, "Minutes_To_Switch_Off", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(45, "Number_Of_Ignitions", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(46, "Active_Temperature", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(47, "Celcius_Or_Fahrenheit", MAESTRO_MESSAGE_TYPE_ONOFF),
    MaestroInformation(48, "Sound_Effects", MAESTRO_MESSAGE_TYPE_ONOFF),
    MaestroInformation(49, "Sound_Effects_State", MAESTRO_MESSAGE_TYPE_ONOFF),
    MaestroInformation(50, "Sleep", MAESTRO_MESSAGE_TYPE_ONOFF),
    MaestroInformation(51, "Mode", MAESTRO_MESSAGE_TYPE_ONOFF),
    MaestroInformation(52, "WifiSondeTemperature1", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(53, "WifiSondeTemperature2", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(54, "WifiSondeTemperature3", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(55, "Unknown", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(56, "SetPuffer", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(57, "SetBoiler", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(58, "SetHealth", MAESTRO_MESSAGE_TYPE_INT),
    MaestroInformation(59, "Return_Temperature", MAESTRO_MESSAGE_TYPE_TEMP),
    MaestroInformation(60, "AntiFreeze", MAESTRO_MESSAGE_TYPE_ONOFF),
    MaestroInformation(-1, "Power", MAESTRO_MESSAGE_TYPE_ONOFF),
    MaestroInformation(-2, "Diagnostics", MAESTRO_MESSAGE_TYPE_ONOFF),
]


def get_maestro_info(frameid: int) -> MaestroInformation:
    """Return Maestro info from the commandlist by name."""
    if 0 <= frameid <= 60:
        return MAESTRO_INFORMATION[frameid]
    _LOGGER.warning("Unknown frameid %s received", frameid)
    return MaestroInformation(
        frameid, "Unknown" + str(frameid), MAESTRO_MESSAGE_TYPE_INT
    )


def get_maestro_infoname(infoname: str) -> MaestroInformation:
    """Return Maestro command from the message list by name."""
    for information in MAESTRO_INFORMATION:
        if infoname == information.name:
            return information
    _LOGGER.warning("Unknown infoname %s received", infoname)
    return MaestroInformation(0, "Unknown", MAESTRO_MESSAGE_TYPE_INT)


def seconds_to_hours_minutes(seconds: int) -> str:
    """Convert second to MCZ format."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:d}:{minutes:02d}:{seconds:02d}"


def get_maestro_state_description(stateid: int) -> str:
    """Return the description of the stove state."""
    for state in MAESTRO_STOVESTATE:
        if stateid == state.stateid:
            return state.description
    _LOGGER.warning("Unknown stateid %s received", stateid)
    return str(stateid)


def get_maestro_power_state(stateid: int) -> bool:
    """Return power state of the stove."""
    for state in MAESTRO_STOVESTATE:
        if stateid == state.stateid:
            return state.onoroff == 1
    _LOGGER.warning("Unknown power state id %s received", stateid)
    return False


def process_infostring(message: str) -> dict:
    """Convert info message."""
    result = {}
    _LOGGER.debug("message to process : %s", message)
    index = 0
    for value in message.split("|"):
        info = get_maestro_info(index)
        if info.messagetype == MAESTRO_MESSAGE_TYPE_TEMP:
            result[info.name] = str(float(int(value, base=16)) / 2)
        elif info.messagetype == MAESTRO_MESSAGE_TYPE_TIMESPAN:
            result[info.name] = seconds_to_hours_minutes(int(value, base=16))
        elif info.messagetype == MAESTRO_MESSAGE_TYPE_3WAY:
            if int(value, base=16) == 1:
                result[info.name] = "Sani"
            else:
                result[info.name] = "Risc"
        elif info.messagetype == MAESTRO_MESSAGE_TYPE_BRAZIER:
            if int(value, base=16) == 0:
                result[info.name] = "OK"
            else:
                result[info.name] = "CLR"
        else:
            result[info.name] = str(int(value, base=16))

        if info.name == "Stove_State":
            result["Power"] = str(get_maestro_power_state(int(result[info.name])))
            result["Diagnostics"] = str(int(result[info.name]) in [30, 48])

        index += 1

    _LOGGER.debug("message proceed to : %s", result)
    return result
