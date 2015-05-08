import os
import sys
import asyncio

from aio.app.runner import runner


def main():
    app_dir = os.path.abspath('apps')
    if not app_dir in sys.path:
        sys.path.append(app_dir)
    loop = asyncio.get_event_loop()
    asyncio.async(
        runner(sys.argv[1:]))
    loop.run_forever()
    loop.close()    


if __name__ == "__main__":
    main()
