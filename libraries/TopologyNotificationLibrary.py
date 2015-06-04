import robot
import socket
from dpkt import ethernet as eth
import struct

LLDP_TYPE_END = 0
LLDP_TYPE_CHASSIS_ID = 1
LLDP_TYPE_PORT_ID = 2
LLDP_TYPE_TTL = 3
LLDP_TYPE_CUSTOM = 127
OPENFLOW_OUI = '\x00\x26\xe1\x00'


def make_lldp_tlv(type, value):
    type = int(type)
    value = bytes(value)
    length = len(value)
    type_length = ((type & 0x7f) << 9) | (length & 0x1ff)
    return struct.pack('>H', type_length) + value


def lldp_local_value(value):
    return '\x07' + value


def make_ncn_lldp_frame(switch_id, port_id, marker,
                        src_mac='\x11\x22\x33\x44\x55\x66',
                        dst_mac='\xaa\xbb\xcc\xdd\xee\xff'):
    payload = (
        make_lldp_tlv(LLDP_TYPE_CHASSIS_ID, lldp_local_value(switch_id)) +
        make_lldp_tlv(LLDP_TYPE_PORT_ID, lldp_local_value(port_id)) +
        make_lldp_tlv(LLDP_TYPE_TTL, '\x00\x00') +
        make_lldp_tlv(LLDP_TYPE_CUSTOM, OPENFLOW_OUI + marker) +
        make_lldp_tlv(LLDP_TYPE_END, ''))
    return eth.Ethernet(src=src_mac, dst=dst_mac, type=0x88cc, data=payload)


def send_frame(interface_name, frame):
    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW) as s:
        s.bind((interface_name, 0))
        s.send(frame.pack())

# example:
# >>> f = make_ncn_lldp_frame('openflow:3', 'openflow:3:1', '\xde\xad\xf0\x0d')
# >>> send_frame('s1-eth1', f)

