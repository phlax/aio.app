import asyncio


class AdditionTestServerProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.transport.write(
            str(
                sum([
                    int(x.strip()) for x in
                    data.decode("utf-8").split("+")])).encode())
        self.transport.close()


@asyncio.coroutine
def test_addition_server(name, protocol, address, port):
    return (
        yield from asyncio.get_event_loop().create_server(
            AdditionTestServerProtocol,
            address, port))
