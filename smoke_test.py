import time

from txml_connector_adapter.dll_wrapper import TXmlConnectorWrapper

def callback(data: str) -> None:
    print("it's callback", data)

connector = TXmlConnectorWrapper("./txmlconnector64.dll")
print(connector.set_callback(callback))
print(connector.initialize("./logs", 2))
print(connector.send_command('<command id="server_status"/>'))
print(connector.send_command('<command id="get_connector_version"/>'))
time.sleep(4)
