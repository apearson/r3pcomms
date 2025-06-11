#!/usr/bin/env python3

import serial
import usb.core
import usb.util
import struct
from operator import xor


class R3PComms:
    """
    River 3 Plus comms from scratch via USB CDC (ACM) and HID
    """

    sequence_num: int
    debug_prints: int
    redact_sn: bool
    serial_number: bytes
    held_xdbg: bytes
    held_dbg: bytes
    s: serial.Serial | None
    u: usb.core.Device | None

    def __init__(self, comport: str = "", usbdev: str = "", debug: int = 0) -> None:
        self.sequence_num = 0
        self.debug_prints = debug

        if comport:
            comms_args = {
                "port": None,
                "baudrate": 115200,
                "bytesize": serial.EIGHTBITS,
                "parity": serial.PARITY_NONE,
                "stopbits": serial.STOPBITS_ONE,
            }
            self.s = serial.Serial(**comms_args)
            self.s.port = comport
            self.s.timeout = 1
        else:
            self.s = None

        if usbdev:
            vid, pid = usbdev.split(":")
            vid = int(vid, 16)
            pid = int(pid, 16)
            self.u = usb.core.find(idVendor=vid, idProduct=pid)
            if self.u is None:
                raise ValueError(
                    f"{hex(vid)}:{hex(pid)} not found. Check Vendor ID and Product ID"
                )
            else:
                if self.debug_prints >= 2:
                    print(f"Found USB device!\n{self.u}")

        else:
            self.u = None

        self.sequence_num = 0
        self.serial_number = b""
        self.redact_sn = True
        self.held_xdbg = b""
        self.held_dbg = b""

    def __enter__(self):
        self.detach_usb_drivers()  # detaches all device interfaces
        self.reattach_usb_drivers()  # reattches everything except the HID interface

        if self.s:
            self.sequence_num = 0
            self.s.open()

        return self

    def __exit__(self, type, value, traceback):
        if self.s:

            self.s.close()
            ret = self.s.__exit__(type, value, traceback)
        else:
            ret = None
        self.reattach_usb_drivers(all=True)
        return ret

    def detach_usb_drivers(self) -> None:
        if self.u is None:
            return

        for cfg in self.u:
            for intf in cfg:
                if self.debug_prints >= 2:
                    print(f"Found USB interface!\n{intf}")
                if self.u.is_kernel_driver_active(intf.bInterfaceNumber):
                    if self.debug_prints >= 2:
                        print(f"Detaching INTERFACE {intf.bInterfaceNumber}")
                    if intf.bInterfaceClass == 0x3 or True:  # HID
                        if self.debug_prints >= 2:
                            print(f"Detaching INTERFACE {intf.bInterfaceNumber}")
                        self.u.detach_kernel_driver(intf.bInterfaceNumber)
                    else:
                        if self.debug_prints >= 2:
                            print(f"Not Detaching INTERFACE {intf.bInterfaceNumber}")
                else:
                    if self.debug_prints >= 2:
                        print(f"No driver on INTERFACE {intf.bInterfaceNumber}")

        # self.u.set_configuration()  # seems to make things unstable

    def reattach_usb_drivers(self, all: bool = False) -> None:
        if self.u is None:
            return

        usb.util.dispose_resources(self.u)
        for cfg in self.u:
            for intf in cfg:
                if self.debug_prints >= 2:
                    print(f"Found USB interface!\n{intf}")
                if self.u.is_kernel_driver_active(intf.bInterfaceNumber):
                    if self.debug_prints >= 2:
                        print(f"No need to attach INTERFACE {intf.bInterfaceNumber}")
                else:
                    if all or intf.bInterfaceClass != 0x3:
                        if self.debug_prints >= 2:
                            print(f"Reattaching INTERFACE {intf.bInterfaceNumber}")
                        self.u.attach_kernel_driver(intf.bInterfaceNumber)

    @staticmethod
    def crc16(data: bytes) -> int:
        """
        CRC-16/ARC
        """
        offset = 0
        length = len(data)
        crc = 0x0000
        for i in range(length):
            crc ^= data[offset + i]
            for j in range(8):
                if (crc & 0x1) == 1:
                    crc = int((crc / 2)) ^ 40961
                else:
                    crc = int(crc / 2)
        return crc & 0xFFFF

    def tx(self, msg: str) -> int | None:
        if self.s:
            overhead_len = 14
            start = 0x03AA

            bmsg = bytes.fromhex(msg)
            msg_len = len(bmsg) - overhead_len
            bsequence = struct.pack("<I", self.sequence_num)
            bmsg_seq = bmsg[:2] + bsequence + bmsg[6:]
            headmsg = struct.pack("<HH", start, msg_len) + bmsg_seq
            crc_val = R3PComms.crc16(headmsg)
            out = headmsg + struct.pack("<H", crc_val)
            if self.debug_prints >= 1:
                print(f">s> {out.hex()}")
            ret = self.s.write(out)
            self.sequence_num += 1
        else:
            ret = None
        return ret

    def rx(self) -> bytes | None:
        ret = None
        if self.s:
            header_len = 4
            base_len = 20

            header = self.s.read(header_len)
            preamble, var_len = struct.unpack("<HH", header)
            payload = self.s.read(base_len + var_len - header_len - 2)
            crc = self.s.read(2)
            full_message = header + payload + crc
            if R3PComms.crc16(full_message) == 0:
                if self.debug_prints >= 1:
                    self.debug_print(full_message)
            else:
                # TODO: gracefully handle this
                raise RuntimeError("CRC check fail")
            ret = header + payload
        return ret

    @staticmethod
    def xorit(data: bytes, sequence_num: int | None = None) -> bytes:
        obfuscattion_offset = 18
        if isinstance(sequence_num, int):
            not_obfuscated = bytes([])
            obfuscated = data
        else:
            not_obfuscated = data[:obfuscattion_offset]
            obfuscated = data[obfuscattion_offset:]
            sequence_num = R3PComms.get_sequencenum(not_obfuscated)

        deobfuscated = bytes([xor(x, sequence_num) & 0xFF for x in obfuscated])
        return not_obfuscated + deobfuscated

    @staticmethod
    def get_sequencenum(data: bytes) -> int:
        offset = 6
        return struct.unpack("<I", data[offset : offset + 4])[0]

    def serial_segmenter(self, source: bytes) -> dict:
        offset = 0
        ssize = len(source)
        result = {}
        while offset < ssize:
            seg_type, seg_len = struct.unpack_from("<HB", source, offset=offset)
            seg_data = source[offset + 3 : offset + 3 + seg_len]
            offset += 3 + seg_len
            if seg_type == 3:
                seg_val = struct.unpack("<I", seg_data)[0]
                name = "Design Capacity?"
                unit = "?"
            elif seg_type == 4:
                seg_val = struct.unpack("<HH", seg_data)
                name = "Capacity?/Battery Voltage?"
                unit = "?"
            elif seg_type == 7:
                seg_val = struct.unpack("f", seg_data)[0]
                name = "Total Load"
                unit = "W"
            elif seg_type == 8:
                seg_val = struct.unpack("f", seg_data)[0]
                name = "Total Draw"
                unit = "W"
            elif seg_type == 9:
                seg_val = struct.unpack("f", seg_data)[0]
                name = "AC Draw"
                unit = "W"
            elif seg_type == 10:
                seg_val = struct.unpack("<HH", seg_data)
                name = "AC Draw Frequency?"
                unit = "Hz"
            elif seg_type == 12:
                seg_val = struct.unpack("f", seg_data)[0]
                name = "Solar/DC Draw"
                unit = "W"
            elif seg_type == 14:
                seg_val = struct.unpack("f", seg_data)[0] * -1
                name = "AC Load"
                unit = "W"
            elif seg_type == 15:
                seg_val = struct.unpack("<HH", seg_data)
                name = "AC Load Frequency?"
                unit = "Hz"
            elif seg_type == 16:
                seg_val = struct.unpack("f", seg_data)[0] * -1
                name = "DC Load"
                unit = "W"
            elif seg_type == 17:
                seg_val = struct.unpack("f", seg_data)[0] * -1
                name = "USB-A Load"
                unit = "W"
            elif seg_type == 18:
                seg_val = struct.unpack("f", seg_data)[0] * -1
                name = "USB-C Load"
                unit = "W"
            elif seg_type == 22:
                seg_val = struct.unpack(f"{seg_len}s", seg_data)[0]
                self.serial_number = seg_val
                if self.debug_print:
                    if self.held_dbg:
                        self.debug_print(self.held_dbg)
                        self.held_dbg = b""
                    if self.held_xdbg:
                        self.debug_print(self.held_xdbg, xord=True)
                        self.held_xdbg = b""
                if self.redact_sn:
                    seg_val = "REDACTED"
                    seg_data = bytes.fromhex("ff") * len(self.serial_number)
                else:
                    seg_val = seg_val.decode()
                name = "Serial Num"
                unit = ""
            elif seg_type == 23:
                seg_val = struct.unpack("<HH", seg_data)
                seg_val = tuple([x / 60 for x in seg_val])
                name = "Time left?"
                unit = "Hr?"
            else:
                seg_val = struct.unpack("f", seg_data)[0]
                name = "unknown-s"
                unit = "?"
            i = 0
            last_name = name
            while name in result:
                name = f"{last_name}{i}"
                i += 1
            result[name] = {
                "type": f"s{seg_type}",
                "data": "0x" + seg_data.hex(),
                "value": seg_val,
                "unit": unit,
            }
        return result

    def query(self, msg: str) -> bytes:
        self.tx(msg)
        rx = self.rx()
        if rx is None:
            raise ValueError(f"Failure getting response to {msg}")
        return rx

    def read_raw_report(self, report_id, length=16) -> bytes | None:
        if self.u:
            try:
                bmRequestType = 0xA1
                bRequest = 0x01
                wValue = (3 << 8) | report_id
                wIndex = 0
                data_or_wLength = length
                if self.debug_prints >= 1:
                    dbg_out = (
                        bmRequestType.to_bytes(1)
                        + bRequest.to_bytes(1)
                        + wValue.to_bytes(2)
                        + wIndex.to_bytes(1)
                        + data_or_wLength.to_bytes(1)
                    )
                    print(f">h> {dbg_out.hex()}")
                data = self.u.ctrl_transfer(
                    bmRequestType=bmRequestType,
                    bRequest=bRequest,
                    wValue=wValue,
                    wIndex=wIndex,
                    data_or_wLength=data_or_wLength,
                )
                data = bytes(data)
                if self.debug_prints >= 1:
                    print(f"<h< {data.hex()}")
                ret = data
            except usb.core.USBError:
                ret = None
        else:
            ret = None

        if ret is None:
            raise ValueError(f"Failure reading report {report_id}")

        return ret

    def get_serial(self) -> dict:
        serial_answer_offset = 19
        answer = self.query("f40d00000000ffff2202010166031600")
        serial_result = self.serial_segmenter(answer[serial_answer_offset:])
        return serial_result

    def ser_get(self) -> dict:
        metrics_answer_offset = 22
        answer = self.query("de2d00000000ffff220201016602")
        xanswer = R3PComms.xorit(answer)
        if self.debug_prints >= 1:
            self.debug_print(xanswer, xord=True)
        metrics_result = self.serial_segmenter(xanswer[metrics_answer_offset:])
        metrics_result["preamble?"] = {
            "type": "pre",
            "data": xanswer[:metrics_answer_offset].hex(),
            "value": 0,
            "unit": "",
        }

        return metrics_result

    def get(self) -> dict:
        metrics = {}
        if self.s:
            metrics |= self.ser_get()
        if self.u:
            metrics |= self.hid_get()
        return metrics

    def hid_get(self) -> dict:
        result = {}
        # for consideration: 12 17 13 11 18 19 1 7
        for rid in (12,):
            data = self.read_raw_report(rid)
            if data:
                report = {}

                if rid == 12:
                    name = "Charge Level"
                    rpt_val = data[1]
                    unit = "%"
                else:
                    name = "unknown-h"
                    rpt_val = data.hex()
                    unit = "?"
                i = 0
                last_name = name
                while name in result:
                    name = f"{last_name}{i}"
                    i += 1
                result[name] = {
                    "type": f"h{rid}",
                    "data": "0x" + data.hex(),
                    "value": rpt_val,
                    "unit": unit,
                }

        return result

    def debug_print(self, data: bytes, xord: bool = False) -> None:
        if xord:
            prompt = "<x< "
        else:
            prompt = "<s< "

        if self.redact_sn and serial:
            if self.serial_number:
                if xord:
                    to_redact = self.serial_number
                else:
                    seq = R3PComms.get_sequencenum(data)
                    to_redact = R3PComms.xorit(self.serial_number, seq)
                data = data.replace(to_redact, bytes.fromhex("ff") * len(to_redact))

                print(prompt + data.hex())
            else:
                if xord:
                    self.held_xdbg = data
                else:
                    self.held_dbg = data
        else:
            print(prompt + data.hex())
