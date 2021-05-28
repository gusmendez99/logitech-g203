#!env/bin/python
import sys
import usb.core
import usb.util
import re
import binascii
from settings import (
    VENDOR_ID,
    DEFAULT_BRIGHTNESS,
    DEFAULT_RATE, 
    PRODIGY_PID,
    PID
)

my_device = None
w_index = None


def help():
    print(
        """Logitech G203 Prodigy / Lightsync Mouse LED control
            Usage:
            \tdriver.py solid {color}
            \tdriver.py cycle {rate} {brightness}
            \tdriver.py breathe {color} {rate} {brightness}
            \tdriver.py intro {on | off}
            \tdriver.py dpi {dpi}
        """
    )


def main():
    if len(sys.argv) < 2:
        help()
        sys.exit()

    args = sys.argv + [None] * (6 - len(sys.argv))

    mode = args[1]
    if mode == "solid":
        set_led_solid(process_color(args[2]))
    elif mode == "cycle":
        set_led_cycle(process_rate(args[2]), process_brightness(args[3]))
    elif mode == "breathe":
        set_led_breathe(
            process_color(args[2]), process_rate(args[3]), process_brightness(args[4])
        )
    elif mode == "intro":
        set_intro_effect(args[2])
    elif mode == "dpi":
        set_dpi(process_dpi(args[2]))
    else:
        print_error("Unknown mode.")


def print_error(msg):
    print("Error: " + msg)
    sys.exit(1)


def process_color(color):
    if not color:
        print_error("No color specified.")
    if color[0] == "#":
        color = color[1:]
    if not re.match("^[0-9a-fA-F]{6}$", color):
        print_error("Invalid color specified.")
    return color.lower()


def process_rate(rate):
    if not rate:
        rate = DEFAULT_RATE
    try:
        return "{:04x}".format(max(1000, min(65535, int(rate))))
    except ValueError:
        print_error("Invalid rate specified.")


def process_brightness(brightness):
    if not brightness:
        brightness = DEFAULT_BRIGHTNESS
    try:
        return "{:02x}".format(max(1, min(100, int(brightness))))
    except ValueError:
        print_error("Invalid brightness specified.")


def process_dpi(dpi):
    if not dpi:
        print_error("No DPI specified.")
    lower_lim = 200

    try:
        return "{:04x}".format(max(lower_lim, min(8000, int(dpi))))
    except ValueError:
        print_error("Invalid DPI specified.")
    return dpi


def set_led_solid(color):
    return set_led("01", color + "0000000000")


def set_led_breathe(color, rate, brightness):
    return set_led("03", color + rate + "00" + brightness + "00")


def set_led_cycle(rate, brightness):
    return set_led("02", "0000000000" + rate + brightness)


def set_led(mode, data):
    global my_device
    global w_index

    prefix = "11ff0e3b00"
    suffix = "000000000000"
    send_command(prefix + mode + data + suffix)


def set_intro_effect(arg):
    if arg == "on" or arg == "1":
        toggle = "01"
    elif arg == "off" or arg == "0":
        toggle = "02"
    else:
        print_error("Invalid value.")

    send_command("11ff0e5b0001" + toggle + "00000000000000000000000000")


def set_dpi(dpi):
    cmd = "10ff0a3b00{}".format(dpi)
    send_command(cmd, disable_ls_onboard_memory=False)



def clear_ls_buffer():
    try:
        while True:
            my_device.read(0x82, 20)
    except usb.core.USBError:
        return


def send_command(data, disable_ls_onboard_memory=False, clear_ls_buf=False):
    attach_mouse()

    if (
        clear_ls_buf
    ):
        clear_ls_buffer()

    if disable_ls_onboard_memory:
        my_device.ctrl_transfer(
            0x21, 0x09, 0x210, w_index, binascii.unhexlify("10ff0e5b010305")
        )
        my_device.read(0x82, 20)

    wValue = 0x211
    if len(data) == 14:
        wValue = 0x210

    my_device.ctrl_transfer(0x21, 0x09, wValue, w_index, binascii.unhexlify(data))
    my_device.read(0x82, 20)

    if data[0:8] == "11ff121b":
        apply_triple_cmd = "11ff127b00000000000000000000000000000000"
        my_device.ctrl_transfer(
            0x21, 0x09, 0x211, w_index, binascii.unhexlify(apply_triple_cmd)
        )
        my_device.read(0x82, 20)

    if (
        clear_ls_buf
    ):
        clear_ls_buffer()

    detach_mouse()


def attach_mouse():
    global my_device
    global w_index
    my_device = usb.core.find(idVendor=VENDOR_ID, idProduct=PID)
    if my_device is None:
        print_error("Device {:04x}:{:04x} not found.".format(VENDOR_ID, PID))
    w_index = 0x01
    if my_device.is_kernel_driver_active(w_index) is True:
        my_device.detach_kernel_driver(w_index)
        usb.util.claim_interface(my_device, w_index)


def detach_mouse():
    global my_device
    global w_index
    if w_index is not None:
        usb.util.release_interface(my_device, w_index)
        my_device.attach_kernel_driver(w_index)
        my_device = None
        w_index = None


if __name__ == "__main__":
    main()
