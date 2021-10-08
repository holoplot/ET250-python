import socket
import argparse
import struct
from sys import exit

parser = argparse.ArgumentParser(description='Control ET 250-3D turntables')
parser.add_argument('--addr', nargs=1, help='The IP address of the ET 250-3D device')
parser.add_argument('--degrees', nargs=1, type=float, help='Degrees to move (for forward and backward commands')
parser.add_argument('--command', nargs=1, help='Command to execute (forward, backward, stop, zero, status)')
parser.add_argument('--send-only', nargs='?', const=True, default=False, help='Only send commands via UDP, and ignore the replies')
args = parser.parse_args()

UDP_PORT = 6668
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if not args.send_only:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", UDP_PORT))

COMMAND_MOVE_FORWARD = 1
COMMAND_MOVE_BACKWARD = 2
COMMAND_STOP = 3
COMMAND_READ_ANGLE = 4
COMMAND_SET_ZERO = 5

REPLY_OK = 0x33
REPLY_ERR = 0x66

STATUS_MOVING = 4
STATUS_STOPPED = 5

def send_command(command, arg = 0):
    checksum = ((command & 0xff) ^ ((arg >> 8) & 0xff)) ^ (arg & 0xff)
    message = struct.pack(">BhB", command, arg, checksum)
    sock.sendto(message, (args.addr[0], UDP_PORT))

    if args.send_only:
        return [REPLY_OK]
    else:
        reply = sock.recvfrom(7)
        return reply[0]

def check_simple_command(reply):
    return reply[0] == REPLY_OK

def move_forward(degree):
    if degree == 0.0:
        return True

    reply = send_command(COMMAND_MOVE_FORWARD, int(degree * 10))
    return check_simple_command(reply)

def move_backward(degree):
    if degree == 0.0:
        return True

    reply = send_command(COMMAND_MOVE_BACKWARD, int(degree * 10))
    return check_simple_command(reply)

def set_zero():
    if args.send_only:
        print("ERROR: The ZERO command does not work in send-only mode")
        return [REPLY_ERR]

    reply = send_command(COMMAND_SET_ZERO)
    return check_simple_command(reply)

def read_angle():
    reply = send_command(COMMAND_READ_ANGLE)
    (status, degree, direction, checksum) = struct.unpack(">BIBB", reply)

    if status == 4:
        status = "moving"
    elif status == 5:
        status = "stopped"

    if direction == 1:
        direction = "counterclockwise"
    elif direction == 2:
        direction = "clockwise"

    print("status= %s dir= %s degree= %.2f" % (status, direction, float(degree / 10)))
    return float(degree / 10)

def move_zero():
    degree = read_angle()
    if (degree > 180):
        move_forward(360 - degree)
    else:
        move_backward(degree)

    return True

def stop():
    reply = send_command(COMMAND_STOP)
    return check_simple_command(reply)

if __name__ == "__main__":
    ret = False

    if args.command[0] == "forward":
        ret = move_forward(args.degrees[0])
    elif args.command[0] == "backward":
        ret = move_backward(args.degrees[0])
    elif args.command[0] == "zero":
        ret = move_zero()
    elif args.command[0] == "stop":
        ret = stop()
    elif args.command[0] == "status":
        ret = True
        read_angle()

    if not ret:
        print("ERROR processing command!")
        exit(1)

    exit(0)
