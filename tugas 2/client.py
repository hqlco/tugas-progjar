import socket
import logging
import time
# rosy haqqy
def send():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.warning("membuka socket")

    server_address = ('172.16.16.101', 45000)
    logging.warning(f"opening socket {server_address}")
    sock.connect(server_address)

    try:
        message = "TIME MESIN:2or3\r\n"
        logging.warning(f"[CLIENT] sending {message}")
        sock.sendall(message.encode("UTF-8"))
        amount_received = 0
        amount_expected = len(message)
        while amount_received < amount_expected:
            data = sock.recv(256)
            amount_received += len(data)
            logging.warning(f"[DITERIMA DARI SERVER] {data}")
        message = "QUIT\r\n"
        logging.warning(f"[CLIENT] sending {message}")
        sock.sendall(message.encode("UTF-8"))
    except Exception as e:
        logging.error(f"Error terjadi: {e}")
    finally:
        logging.warning("closing")
        sock.close()
    return


if __name__=='__main__':
    while(True):
        send()
        time.sleep(1)