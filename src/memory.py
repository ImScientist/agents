"""
    Initial setup of Postgres DB used as a checkpointer of the Graph
"""
import os
import sys
import logging
from langgraph.checkpoint.postgres import PostgresSaver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

if __name__ == '__main__':
    try:
        POSTGRES_CONN_STRING = os.environ['POSTGRES_CONN_STRING']
    except KeyError:
        logger.error('POSTGRES_CONN_STRING environment variable is required')
        sys.exit(1)

    logger.info('Initial setup of the Postgres DB....')

    try:
        with PostgresSaver.from_conn_string(POSTGRES_CONN_STRING) as checkpointer:
            checkpointer.setup()
        logger.info('Initial setup of the Postgres DB done.')
    except Exception as e:
        logger.error(f'Failed to setup Postgres DB: {e}')
        sys.exit(1)
