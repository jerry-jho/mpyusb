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

def CtrlTransfer(device, desc_type, index, buf, flag=0, language_id=0):
    wValue = desc_type << 8 | index
    wIndex = language_id
    device.ctrl_transfer(
        _REQ_RCPT_DEVICE | _REQ_TYPE_STANDARD | _DIR_IN | flag,
        _REQ_GET_DESCRIPTOR,
        wValue,
        wIndex,
        buf,
    )


def GetConfigurationDescriptor(device, index):
    buf = bytearray(4)
    CtrlTransfer(device, DESC_CONFIGURATION, index, buf)
    #utils.print_bytearray(buf)
    wTotalLength = struct.unpack("<xxH", buf)[0]
    full_buf = bytearray(wTotalLength)
    #print(f"get_configuration_descriptor: length = {wTotalLength}")
    CtrlTransfer(device, DESC_CONFIGURATION, index, full_buf)
    return full_buf

def GetHidReport(device, index, length):
    full_buf = bytearray(length)
    CtrlTransfer(device, DESC_HID_TYPE_REPORT, index, full_buf, 1)
    return full_buf

def InterfaceClassStr(c):
    if c == 0x03:
        return 'HID(0x03)'
    return f'Other(0x{c:02X})'

def InterfaceSubClassStr(c):
    if c == 0x01:
        return 'Boot(0x01)'
    return f'Other(0x{c:02X})'

def InterfaceProtocalStr(c):
    if c == 0x02:
        return 'Mouse(0x02)'
    if c == 0x01:
        return 'Keyboard(0x01)'
    return f'Other(0x{c:02X})'

def HIDTypeStr(c):
    if c == 0x22:
        return 'Report(0x22)'
    return f'Other(0x{c:02X})'

class EnumDeviceType:
    BootKeyboard = 1
    BootMouse = 2
    Other = 0

class HIDInterface:
    def __init__(self):
        self.Index = None
        self.DeviceType = None
        self.HIDReportSize = None
        self.EndpointAddresses = []
    def __repr__(self):
        return f"HIDInterface(Index={self.Index} DeviceType={self.DeviceType} HIDReportSize={self.HIDReportSize} EndpointAddresses={self.EndpointAddresses})"

def GetHIDInterfaces(desc, print_raw=False, print_info=False):
    if print_raw:
        print("[DESC] Raw Bytes:")
        utils.print_bytearray(desc)
    rtn = []
    current_interface = None
    i = 0
    if_index = 0
    while i < len(desc):
        bLength = desc[i]
        bDescriptorType = desc[i + 1]
        if bDescriptorType == DESC_CONFIGURATION:
            bNumInterfaces = int(desc[i + 4])
            if print_info:
                print(f"[CONFIGURATION]\n  bNumInterfaces={bNumInterfaces}")
        elif bDescriptorType == DESC_INTERFACE:
            bInterfaceNumber = int(desc[i + 2])
            bNumEndpoints = int(desc[i + 4])
            bInterfaceClass = int(desc[i + 5])
            bInterfaceSubClass = int(desc[i + 6])
            bInterfaceProtocol = int(desc[i + 7])
            if print_info:
                print(f"  [INTERFACE {bInterfaceNumber}]")
                print(f"    bNumEndpoints={bNumEndpoints}")
                print(f"    Attr={utils.InterfaceClassStr(bInterfaceClass)}.{utils.InterfaceSubClassStr(bInterfaceSubClass)}.{utils.InterfaceProtocalStr(bInterfaceProtocol)}")
            if bInterfaceClass == 3:
                if current_interface is not None:
                    rtn.append(current_interface)
                current_interface = HIDInterface()
                current_interface.Index = if_index
                if_index += 1
                current_interface.DeviceType = bInterfaceProtocol

        elif bDescriptorType == DESC_HID:
            bHIDType = int(desc[i + 6])
            bHIDLength = int(desc[i + 7])
            if bHIDType == 0x22:
                current_interface.HIDReportSize = bHIDLength
            if print_info:
                print(f"  [HID]")
                print(f"    bHIDLength={bHIDLength}")
                print(f"    Attr={utils.HIDTypeStr(bHIDType)}")
        elif bDescriptorType == DESC_ENDPOINT:
            bEndpointAddress = int(desc[i + 2])
            current_interface.EndpointAddresses.append(bEndpointAddress)
            if print_info:
                print(f"  [ENDPOINT]")
                print(f"    bEndpointAddress=0x{bEndpointAddress:02X}")
        i += bLength
    if current_interface is not None:
        rtn.append(current_interface)
    return rtn

def FilterInterface(hid_interfaces):
    if len(hid_interfaces) == 0:
        return None
    if len(hid_interfaces) == 1:
        return hid_interfaces[0]
    for hif in hid_interfaces:
        if hif.DeviceType != EnumDeviceType.Other:
            return hif
    return hid_interfaces[0]