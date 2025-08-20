"""
    Initial setup of Postgres DB used as a checkpointer of the Graph
"""
import os
import logging
from langgraph.checkpoint.postgres import PostgresSaver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

POSTGRES_CONN_STRING = os.environ['POSTGRES_CONN_STRING']

if __name__ == '__main__':
    logger.info('Initial setup of the Postgres DB....')

    with PostgresSaver.from_conn_string(POSTGRES_CONN_STRING) as checkpointer:
        checkpointer.setup()

    logger.info('Initial setup of the Postgres DB done.')
