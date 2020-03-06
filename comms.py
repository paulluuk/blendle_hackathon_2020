from subprocess import Popen, PIPE


class InteractiveSession:
    def __init__(self, python_or_ruby, path):
        # this subprocess is pretty shake, it will
        # get stuck if the subprocess does not behave
        # exactly as expected.
        self.process = self.start([python_or_ruby, path])

    def start(self, execute_cmd):
        # start a new subprocess
        return Popen(
            execute_cmd,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        )

    def read(self):
        # read from the subprocess' output
        response = self.process.stdout.readline().decode("utf-8").strip()
        print("(output) {}".format(response))
        return response

    def write(self, message):
        # write to the subprocess' input
        print("(input)  {}".format(message))
        self.process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
        self.process.stdin.flush()

    def terminate(self):
        # close the subprocess
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)
