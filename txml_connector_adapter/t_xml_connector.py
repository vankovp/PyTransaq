from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from loguru import logger
from pydantic import BaseModel


from txml_connector_adapter.dll_wrapper import TXmlConnectorWrapper

_DEFAULT_FINAM_HOST = "tr1.finam.ru"

class ConnectionSettings(BaseModel):
    login: str
    password: str
    host: str = _DEFAULT_FINAM_HOST
    port: int = 3900
    rqdelay: int = 100
    session_timeout: int = 25
    request_timeout: int = 10


class TXmlConnector:
    _t_xml_connector_wrapper: TXmlConnectorWrapper
    _connection_settings: ConnectionSettings
    _logs_dir: Path
    _log_level: int
    _queue: Queue

    def __init__(
        self,
        t_xml_connector_wrapper: TXmlConnectorWrapper,
        connection_settins: ConnectionSettings,
        logs_dir: Path = "./logs",
        log_level: int = 3
    ):
        self._t_xml_connector_wrapper = t_xml_connector_wrapper
        self._connection_settings = connection_settins
        self._logs_dir = logs_dir
        self._log_level = log_level
        self._queue = Queue()

    @property
    def _login_command(self) -> str:
        return f"""
            <command id="connect">
                <login>{self._connection_settings.login}</login>
                <password>{self._connection_settings.password}</password>
                <host>{self._connection_settings.host}</host>
                <port>{self._connection_settings.port}</port>
                <rqdelay>{self._connection_settings.rqdelay}</rqdelay>
                <session_timeout>{self._connection_settings.session_timeout}</session_timeout>
                <request_timeout>{self._connection_settings.request_timeout}</request_timeout>
            </command>
        """
        # .replace("\n", "").replace("    ", "")

    def _callback(self, data: str) -> bool:
        self._queue.put(data)

    def send_command(self, comamnd: str) -> str | Exception:
        logger.debug(f"Sending command: {comamnd}")
        result = self._t_xml_connector_wrapper.send_command(comamnd)
        if result.find('success="true"') == -1:
            # failed to execute command
            return Exception("Failed to execute command")
        responce = self._queue.get(timeout=None)
        logger.debug(f"Recieved responce: {responce}")
        assert isinstance(responce, str)
        return responce

    def init(self):
        self._t_xml_connector_wrapper.set_callback(self._callback)
        self._t_xml_connector_wrapper.initialize(self._logs_dir, self._log_level)
        login_result = self.send_command(self._login_command)
        if isinstance(login_result, Exception):
            raise login_result
        