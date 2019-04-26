from concurrent import futures
import time
import os
import traceback
import cx_Oracle
from loguru import logger

import grpc

import select_pb2
import select_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_MAX_WORKERS = os.getenv('SELECT_MAX_WORKERS') or 20
_PORT = os.getenv('SELECT_PORT') or 50051
_USER_NAME = os.getenv('SELECT_USER_NAME') or 'orcl'
_PASSWORD = os.getenv('SELECT_PASSWORD') or 'orcl'
_DATABASE_URL = os.getenv('SELECT_DATABASE_URL') or '127.0.0.1:1521/orcl'


class Greeter(select_pb2_grpc.GreeterServicer):


    def _execute_sql(sql, fetch=True, **kw):
        logger.info('execute sql is: %s' % sql)
        con = None
        cursor = None
        result = None
        try:
            con = cx_Oracle.connect(_USER_NAME, _PASSWORD, _DATABASE_URL)
            cursor = con.cursor()
            cursor.prepare(sql)
            cursor.execute(None, kw)
            if fetch:
                result = cursor.fetchall()
            else:
                con.commit()
        except Exception as e:
            logger.error(traceback.format_exc())
            if con is not None:
                con.rollback()
        finally:
            if cursor is not None:
                cursor.close()
            if con is not None:
                con.close()
        return result

    def SelectDatabase(self, request, context):
        logger.info("sql=[{}]", request.sql)
        execute_result = self._execute_sql(request.sql)
        final_result = [];
        if execute_result is not None:
            for item in execute_result:
                final_result.append(select_pb2.SelectReply.Result(
                    fields=[str(p) for p in item]))
        return select_pb2.SelectReply(results=final_result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS))
    select_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:{}'.format(_PORT))
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logger.add("logs/select_orcl.log", rotation="1 day", level="INFO")
    serve()
