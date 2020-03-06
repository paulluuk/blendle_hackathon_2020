from subprocess import Popen, PIPE


class InteractiveSession:
    def __init__(self, python_or_ruby, path):
        self.process = self.start([python_or_ruby, path])

    def start(self, executable_file):
        return Popen(
            executable_file,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        )

    def read(self):
        response = self.process.stdout.readline().decode("utf-8").strip()
        print("(output) {}".format(response))
        return response

    def write(self, message):
        print("(input)  {}".format(message))
        self.process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
        self.process.stdin.flush()

    def terminate(self):
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)
