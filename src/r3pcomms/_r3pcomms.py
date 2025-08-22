#!/usr/bin/env python3

import serial
import hid
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
    h: hid.device | None
    hid_path: str

    def __init__(self, comport: str = "", hiddev: str = "", debug: int = 0) -> None:
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

        if hiddev:
            vid, pid = hiddev.split(":")
            vid = int(vid, 16)
            pid = int(pid, 16)
            self.hid_path = self.find_hid_device(pid, vid)
            if self.hid_path:
                self.h = hid.device()
                if self.debug_prints >= 2:
                    print(f"Found HID device: {self.hid_path}")
            else:
                raise ValueError(
                    f"{hex(vid)}:{hex(pid)} not found. Check Vendor ID and Product ID"
                )
        else:
            self.h = None

        self.sequence_num = 0
        self.serial_number = b""
        self.redact_sn = True
        self.held_xdbg = b""
        self.held_dbg = b""

    def __enter__(self):
        if self.s:
            self.sequence_num = 0
            self.s.open()
        if self.h:
            self.h.open_path(self.hid_path)

        return self

    def __exit__(self, type, value, traceback):
        if self.h:
            self.h.close()
        if self.s:
            self.s.close()
            ret = self.s.__exit__(type, value, traceback)
        else:
            ret = None
        return ret

    def find_hid_device(self, pid: str, vid: str) -> str | None:
        ret = None
        devices = hid.enumerate()
        for device in devices:
            if device["vendor_id"] == vid and device["product_id"] == pid:
                if "hidraw" in device["path"].decode("utf-8"):
                    ret = device["path"]
        return ret

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
                name = "Design Charge Capacity"
                unit = "mAh"
            elif seg_type == 4:
                seg_val = struct.unpack("<BBBB", seg_data)
                name = "Operational Flags/Temperature?"
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
            elif seg_type == 13:
                seg_val = struct.unpack("<L", seg_data)[0] / 10
                name = "Line Frequency?"
                unit = "Hz"
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
                unit = "Hr"
            elif seg_type == 25:
                seg_val = seg_data.hex()
                name = "Mfg. Model/Batch/Date?"
                unit = "?"
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
        if self.h:
            try:
                if self.debug_prints >= 1:
                    dbg_out = (report_id.to_bytes(1), length.to_bytes(1))
                    print(f">h> {dbg_out[0].hex()}{dbg_out[1].hex()}")
                data = self.h.get_feature_report(report_id, length)
                data = bytes(data)
                if self.debug_prints >= 1:
                    print(f"<h< {data.hex()}")
                ret = data
            except Exception as e:
                raise ValueError(f"Failure reading report {report_id}: {e}")
        else:
            ret = None

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
        if self.h:
            metrics |= self.hid_get()
        return metrics

    def hid_get(self) -> dict:
        result = {}
        # for consideration: 12 17 13 11 18 19 1 7
        to_read = (12, 17, 13, 11, 18, 19, 1, 7)
        # to_read.append((12, 16))  # Cnst,Var,Abs,Vol
        # to_read.append((17, 16))  # Data,Var,Abs,NoPref,Vol
        # to_read.append((13, 16))  # Cnst,Var,Abs,NoPref,Vol
        # to_read.append((11, 16))  # Cnst,Var,Abs,NoPref
        # to_read.append((18, 16))  # Data,Var,Abs,NoPref,Vol
        # to_read.append((19, 16))  # Data,Var,Abs,NoPref,Vol
        # to_read.append((1,  128))  # Cnst,Var,Abs,Vol
        # to_read.append((7,  1))  #
        for rid in to_read:
            data = self.read_raw_report(rid)
            if data:
                report = {}
                payload = data[1:]
                if rid == 12:
                    name = "Charge Level"
                    rpt_val = payload[0]
                    unit = "%"
                elif rid == 13:
                    name = "Flags/Operation Mode?"
                    val = payload.hex()
                    if val == "2d00":
                        rpt_val = "Discharging"
                    elif val == "3317":
                        rpt_val = "Charging"
                    else:
                        rpt_val = "Unknown"
                    unit = ""
                else:
                    name = "unknown-h"
                    rpt_val = payload.hex()
                    unit = "?"
                i = 0
                last_name = name
                while name in result:
                    name = f"{last_name}{i}"
                    i += 1
                result[name] = {
                    "type": f"h{rid}",
                    "data": "0x" + payload.hex(),
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
