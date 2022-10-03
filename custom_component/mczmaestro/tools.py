"""MCZ tools."""
import websocket

from .const import MAESTRO_INFORMATION, MAESTRO_STOVESTATE


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


def get_maestro_info(frameid: int) -> MaestroInformation:
    """Return Maestro info from the commandlist by name."""
    if 0 >= frameid <= 60:
        return MAESTRO_INFORMATION[frameid]
    return MaestroInformation(frameid, "Unknown" + str(frameid), "int")


def get_maestro_infoname(infoname: str) -> MaestroInformation:
    """Return Maestro command from the message list by name."""
    for information in MAESTRO_INFORMATION:
        if infoname == information.name:
            return information
    return MaestroInformation(0, "Unknown", "int")


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
    return str(stateid)


def get_maestro_power_state(stateid: int) -> bool:
    """Return power state of the stove."""
    for state in MAESTRO_STOVESTATE:
        if stateid == state.stateid:
            return state.onoroff == 1
    return False


def process_infostring(message: str) -> dict:
    """Convert info message."""
    res = {}
    for i in range(1, len(message.split("|"))):
        info = get_maestro_info(i)
        if info.messagetype == "temperature":
            res[info.name] = str(float(int(message.split("|")[i], 16)) / 2)
        elif info.messagetype == "timespan":
            res[info.name] = seconds_to_hours_minutes(int(message.split("|")[i], 16))
        elif info.messagetype == "3way":
            if int(message.split("|")[i], 16) == 1:
                res[info.name] = "Sani"
            else:
                res[info.name] = "Risc"
        elif info.messagetype == "brazier":
            if int(message.split("|")[i], 16) == 0:
                res[info.name] = "OK"
            else:
                res[info.name] = "CLR"
        else:
            res[info.name] = str(int(message.split("|")[i], 16))

        if info.name == "Stove_State":
            res["Power"] = str(get_maestro_power_state(int(res[info.name])))
            res["Diagnostics"] = str(int(res[info.name]) in [30, 48])

    return res
