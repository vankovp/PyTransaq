from transaq import TransaqConnector

login = 'FZTC19829A'
ip = 'localhost'
def test():
    tConnector = TransaqConnector(ip)
    if tConnector.connect(login):
        #tConnector.get_status()
        #tConnector.get_old_news()
        try:
            print(tConnector.get_markets())
            print(tConnector.get_securities_info('1', 'RU000A0JS603'))



            
        except Exception as e:
            print(e)

        # print(tConnector.get_element_value('client'))
        # tConnector.get_servtime_difference()
        # print(tConnector.get_connector_version())
        # print(tConnector.get_server_id())

        tConnector.disconnect()
        tConnector.close()


if __name__ == '__main__':
    test()
