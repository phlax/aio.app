import os
import asyncio
import logging.config
from configparser import ConfigParser, ExtendedInterpolation

import aio.config


@asyncio.coroutine
def start_logging(config):
    # combine system config with any logging config
    parser = ConfigParser(interpolation=ExtendedInterpolation())
    parser.read_dict(aio.config.replicate_config(config))

    if os.path.exists('logging.conf'):
        parser.read_file(open('logging.conf'))

    # filter out the logging sections
    logging_sections = ['handler', 'logger', 'formatter']
    logging_config = aio.config.replicate_config(
        parser,
        test_section=lambda section: (
            any([section.startswith(x) for x in logging_sections])))
    logging_parser = ConfigParser()
    logging_parser.read_dict(logging_config)
    loggers = []
    formatters = []
    handlers = []
    for section, options in logging_parser.items():
        if section.startswith('logger_'):
            loggers.append(section[7:])
        if section.startswith('formatter_'):
            formatters.append(section[10:])
        if section.startswith('handler_'):
            handlers.append(section[8:])
    logging_parser['loggers']['keys'] = ','.join(loggers)
    logging_parser['formatters']['keys'] = ','.join(formatters)
    logging_parser['handlers']['keys'] = ','.join(handlers)
    logging.config.fileConfig(logging_parser)
