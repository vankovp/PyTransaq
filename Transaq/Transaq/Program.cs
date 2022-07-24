using System;

namespace Transaq
{
    class Program
    {
        static void Main()
        {
            Ports.commandListenerPort = Int32.Parse("11000");
            Ports.PingPort = Int32.Parse("11001");
            Ports.newsListenerPort = Int32.Parse("11002");
            Ports.subscribeDataListenerPort = Int32.Parse("11003");
            Ports.dataListenerPort = Int32.Parse("11004");
            Ports.accountListenerPort = Int32.Parse("11005");

            Server server = new Server();
            server.Run();
        }
    }
}
