import os
import asyncio

import aio.testing
from aio.app.testing import AioAppTestCase
from aio.app.runner import runner
from aio.core.exceptions import MissingConfiguration

test_dir = os.path.dirname(__file__)


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

SERVER_CONFIG_NO_FACTORY_OR_PROTOCOL = """
[server/test]
port: 7070
address: 127.0.0.1
"""

SERVER_CONFIG_NO_PORT = """
[server/test]
factory: aio.app.tests.test_run_servers.test_addition_server
"""

SERVER_CONFIG_FACTORY = """
[server/test]
port: 7070
factory: aio.app.tests.test_run_servers.test_addition_server
"""

SERVER_CONFIG_PROTOCOL = """
[server/test]
port: 7070
protocol: aio.app.tests.test_run_servers.AdditionTestServerProtocol
"""


class RunCommandServersTestCase(AioAppTestCase):

    def test_run_servers_no_factory_or_protocol(self):

        @aio.testing.run_forever
        def run_server():
            yield from runner(
                ['run'],
                config_string=SERVER_CONFIG_NO_FACTORY_OR_PROTOCOL)

        with self.assertRaises(MissingConfiguration):
            run_server()

    def test_run_servers_no_port(self):

        @aio.testing.run_forever
        def run_server():
            yield from runner(
                ['run'],
                config_string=SERVER_CONFIG_NO_PORT)

        with self.assertRaises(MissingConfiguration):
            run_server()

    @aio.testing.run_forever
    def test_run_servers_factory(self):
        yield from runner(
            ['run'],
            config_string=SERVER_CONFIG_FACTORY)

        @asyncio.coroutine
        def test_cb():
            reader, writer = yield from asyncio.open_connection(
                '127.0.0.1', 7070)
            writer.write(b'2 + 2 + 3')
            yield from writer.drain()
            result = yield from reader.read()
            self.assertEqual(int(result), 7)

        return test_cb

    @aio.testing.run_forever
    def test_run_servers_protocol(self):
        yield from runner(
            ['run'],
            config_string=SERVER_CONFIG_PROTOCOL)

        @asyncio.coroutine
        def test_cb():
            reader, writer = yield from asyncio.open_connection(
                '127.0.0.1', 7070)
            writer.write(b'2 + 2 + 3')
            yield from writer.drain()
            result = yield from reader.read()
            self.assertEqual(int(result), 7)

        return test_cb
