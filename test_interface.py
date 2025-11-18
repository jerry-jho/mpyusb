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
        for hid_interface in interfaces:
            hid_desc = usbhid.GetHidReport(device, hid_interface.Index, hid_interface.HIDReportSize)
            print(f"HID Report of Interface {hid_interface.Index}")
            utils.print_bytearray(hid_desc)
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)
        device.set_configuration()
        bloop = True
        prev_rbuf_hive = {}
        while(bloop):
            for hid_interface in interfaces:
                for i in range(len(hid_interface.EndpointAddresses)):
                    rbuf = usbhid.Read(device, hid_interface.EndpointAddresses[i], hid_interface.EndpointSizes[i])
                    if not utils.is_all_zero(rbuf):
                        prev_rbuf = prev_rbuf_hive.get(f"{hid_interface.Index}:{i}", None)
                        if not utils.is_equal(prev_rbuf, rbuf):
                            print(f"Device Type {hid_interface.DeviceType} Interface {hid_interface.Index} Endpoint {i} ", end="")
                            utils.print_bytearray(rbuf)
                        prev_rbuf_hive[f"{hid_interface.Index}:{i}"] = rbuf
                        if hid_interface.DeviceType == usbhid.EnumDeviceType.BootKeyboard and rbuf[2] == 0x29:
                            bloop = False
                        if hid_interface.DeviceType == usbhid.EnumDeviceType.BootMouse and rbuf[0] == 0x02:
                            bloop = False
        device_found = True
    
    