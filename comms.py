from subprocess import Popen, PIPE
from threading import Timer

class InteractiveSession:
    def __init__(self, python_or_ruby, path):
        # this subprocess is pretty shake, it will
        # get stuck if the subprocess does not behave
        # exactly as expected.
        self.process = self.start([python_or_ruby, path])

    def start(self, execute_cmd):
        print("Starting fighter communications..")
        # start a new subprocess
        return Popen(
            execute_cmd,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        )

    def read_within_time(self, source, seconds):
        # give the process 5 seconds to respond, otherwise we kill it.
        timer = Timer(interval=seconds, function=self.terminate)
        try:
            timer.start()
            if source == self.process.stdout:
                stdout = source.readline()
                response = stdout.decode("utf-8").strip()
            elif source == self.process.stderr:
                stderr = source.readlines()
                response = "\n"+"\n".join([line.decode("utf-8").strip() for line in stderr])
        finally:
            timer.cancel()
        return response

    def read(self):
        # read from the subprocess' output

        response = self.read_within_time(self.process.stdout, 5)
        if len(response) == 0:
            response_error = self.read_within_time(self.process.stderr, 1)
            if len(response_error) > 0:
                raise(Exception("Fighter failed to respond in time. It returned this error: {}".format(response_error)))
            else:
                raise(Exception("Fighter failed to respond in time. It returned no error."))
        return response

    def write(self, message):
        # write to the subprocess' input
        self.process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
        self.process.stdin.flush()

    def terminate(self):
        # close the subprocess
        print("Closing fighter communications..")
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)
