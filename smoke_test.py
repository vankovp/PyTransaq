import pydantic

from txml_connector_adapter.dll_wrapper import TXmlConnectorWrapper
from txml_connector_adapter.t_xml_connector import ConnectionSettings, TXmlConnector


class Config(pydantic.BaseModel):
    connection: ConnectionSettings


with open("config.json", "r") as file:
    config = pydantic.parse_raw_as(Config, file.read())

dll_wrapper = TXmlConnectorWrapper("./txmlconnector64.dll")
connector = TXmlConnector(dll_wrapper, config.connection)

connector.init()
print("Connector initialized")
print("Connector version:", connector.send_command('<command id="get_connector_version"/>'))
