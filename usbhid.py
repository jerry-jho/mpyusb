import struct
from micropython import const
import utils

_DIR_OUT = const(0x00)
_DIR_IN = const(0x80)
_REQ_RCPT_DEVICE = const(0)
_REQ_TYPE_STANDARD = const(0x00)
_REQ_GET_DESCRIPTOR = const(6)

DESC_DEVICE = 0x01
DESC_CONFIGURATION = 0x02
DESC_STRING = 0x03
DESC_INTERFACE = 0x04
DESC_ENDPOINT = 0x05
DESC_HID = 0x21

DESC_HID_TYPE_REPORT = 0x22

def get_descriptor(device, desc_type, index, buf, flag=0, language_id=0):
    wValue = desc_type << 8 | index
    wIndex = language_id
    device.ctrl_transfer(
        _REQ_RCPT_DEVICE | _REQ_TYPE_STANDARD | _DIR_IN | flag,
        _REQ_GET_DESCRIPTOR,
        wValue,
        wIndex,
        buf,
    )


def get_configuration_descriptor(device, index):
    buf = bytearray(4)
    get_descriptor(device, DESC_CONFIGURATION, index, buf)
    #utils.print_bytearray(buf)
    wTotalLength = struct.unpack("<xxH", buf)[0]
    full_buf = bytearray(wTotalLength)
    #print(f"get_configuration_descriptor: length = {wTotalLength}")
    get_descriptor(device, DESC_CONFIGURATION, index, full_buf)
    return full_buf

def get_hid_report(device, index, length):
    full_buf = bytearray(length)
    get_descriptor(device, DESC_HID_REPORT_DESCRIPTOR, index, full_buf, 1)
    return full_buf