import time
import functools
import grpc

def retry_on_failure(retries=12):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(self, *args, **kwargs):
            last_exception = None
            for _ in range(retries):
                try:
                    return func(self, *args, **kwargs)
                except grpc.RpcError as e:
                    last_exception = e
                    print(f"Unable to connect to leader server when making request. Will try to update leader and retry")
                    time.sleep(1)
                    self._update_leader()  # Update leader in case it has changed
            raise last_exception
        return wrapper_retry
    return decorator_retry