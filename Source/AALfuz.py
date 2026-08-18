import socket, time, os, subprocess
from aalpy.base import SUL
from aalpy.learning_algs import run_stochastic_Lstar
from aalpy.oracles import RandomWalkEqOracle
from aalpy.utils import visualize_automaton, save_automaton_to_file

FTP_HOST = "127.0.0.1"
FTP_PORT = 2200

A = [
    "USER ubuntu",
    "PASS ubuntu",
    "NOOP",
    "SYST",
    "FEAT",
    "PWD",
    "HELP",
    "TYPE I",
    "PASV",
    "EPSV",
    "CWD /",
    "CDUP",
    "LIST",
    "MLSD",
    "PORT 127,0,0,1,132,209",
    "SIZE file",
    "RETR file",
    "APPE file",
    "RNFR file",
    "RNTO file",
    "DELE file",
    "MKD dir",
    "RMD dir",
    "REST 0",
    "ABOR",
    "AUTH TLS",
    "PBSZ 0",
    "PROT P",
    "OPTS UTF8 ON",
    "SITE HELP",
    "QUIT",
    "STOR",
]

class LightFTPSUL(SUL):
    def __init__(self):
        super().__init__()
        self.sock = None
        self.proc = None

    def pre(self):
        if getattr(self, "sock", None) is not None:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                self.sock.close()
            except OSError:
                pass

            self.sock = None

        self._start_fttp()

        for attempt in range(50):
            try:
                sock = socket.socket()
                sock.settimeout(5)
                sock.connect((FTP_HOST, FTP_PORT))
                self.sock = sock
                break
            except (ConnectionRefusedError, ConnectionResetError):
                sock.close()
                time.sleep(0.1)
        else:
            raise RuntimeError("Could not connect to LightFTP")

        data = self.sock.recv(1024)
        print(f"Banner: {data!r}")

    def post(self):
        try:
            self.sock.close()
        except:
            pass
        self._stop_fttp()

    def step(self, letter):
        message = (letter + "\r\n").encode()
        print(message)
        resp = "NO_RESP"

        try:
            self.sock.sendall(message)
            reply = self._recv_reply()
            print(f"RAW REPLY: {repr(reply)}")
            resp = reply.strip()[:3]
            if resp == '':
                resp = "NO_RESP"
        except Exception:
            pass
        print(resp)
        return resp

    def _recv_reply(self):
        data = b''
        self.sock.settimeout(1)

        while True:
            try:
                chunk = self.sock.recv(1024)
                if not chunk:
                    break
                data += chunk

                if b"\r\n" in data:
                    break

            except socket.timeout:
                break

        return data.decode(errors="ignore")

    def _start_fttp(self):
        base = os.path.dirname(os.path.abspath(__file__))
        fttp_path = os.path.join(base, "fftp")
        fttp_conf_path = os.path.join(base, "fftp.conf")

        self.proc = subprocess.Popen(
            [fttp_path, fttp_conf_path, str(FTP_PORT)],
            stdout=subprocess.DEVNULL
        )

    def _stop_fttp(self):
        if self.proc and self.proc.poll() is None:  
            self.proc.terminate()                   
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()                    
                self.proc.wait()
   

def main():
    sul = LightFTPSUL()
    eq_oracle = RandomWalkEqOracle(
        A,
        sul,
        num_steps = 10,
    )

    learned_model = run_stochastic_Lstar(
        A,
        sul,
        eq_oracle = eq_oracle,
        automaton_type = "smm",
        print_level = 3, 
    )

    visualize_automaton(learned_model, path="AALfuz_output_Lstar_smm")
    save_automaton_to_file(learned_model)

if __name__ == "__main__":
    main()
