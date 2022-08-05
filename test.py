from transaq import TransaqConnector

login = 'FZTC19829A'
ip = '192.168.0.240'
def test():
    tConnector = TransaqConnector(ip)
    tConnector.disconnect()
    if tConnector.connect(login):
        #tConnector.get_status()
        #tConnector.get_old_news()
        print(tConnector.get_element_value('client'))
        tConnector.get_servtime_difference()
        print(tConnector.get_connector_version())
        print(tConnector.get_server_id())

        tConnector.disconnect()
        tConnector.close()


if __name__ == '__main__':
    test()
