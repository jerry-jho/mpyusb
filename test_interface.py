import board
import max3421e
import time
import usb
import busio
import array
import usbhid
import utils

spi = busio.SPI(clock = board.IO18, MOSI = board.IO23, MISO = board.IO19)
cs = board.IO32
irq = board.I35
host_chip = max3421e.Max3421E(spi, chip_select=cs, irq=irq)

device_found = False

while not device_found:
    print("Finding devices:")
    time.sleep(5)
    for device in usb.core.find(find_all=True):
        print(f"{device.idVendor:04x}:{device.idProduct:04x}: {device.manufacturer} {device.product}")
        desc = usbhid.GetConfigurationDescriptor(device, 0)
        interfaces = usbhid.GetHIDInterfaces(desc)
        print(interfaces)
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)
        device.set_configuration()
        hid_interface = usbhid.FilterInterface(interfaces)
        if hid_interface.DeviceType == usbhid.EnumDeviceType.BootKeyboard:
            rbuf = array.array("b", [0x00] * 0x08)
            print("Press Keyboard, ESC to quit")
            while(1):
                count = 0
                try:
                    count = device.read(hid_interface.EndpointAddresses[0], rbuf, timeout=10)
                except usb.core.USBTimeoutError:
                    continue
                if count > 0:
                    utils.print_bytearray(rbuf)
                    if rbuf[2] == 0x29:
                        break
        elif hid_interface.DeviceType == usbhid.EnumDeviceType.BootMouse:
            rbuf = array.array("b", [0x00] * 0x08)
            print("Press Mouse, Right Click to quit")
            while(1):
                count = 0
                try:
                    count = device.read(hid_interface.EndpointAddresses[0], rbuf, timeout=10)
                except usb.core.USBTimeoutError:
                    continue
                if count > 0:
                    utils.print_bytearray(rbuf)
                    if rbuf[0] == 0x02:
                        break
        else:
            hid_desc = usbhid.GetHidReport(device, hid_interface.Index, hid_interface.HIDReportSize)
            utils.print_bytearray(hid_desc)
        device_found = True
    
    