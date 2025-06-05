#!/usr/bin/env python3

import serial
import struct
from operator import xor


class R3PComms(serial.Serial):
    """
    River 3 Plus comms from scratch via USB CDC (ACM)
    """

    sequence_num: int
    debug_prints: bool
    redact_sn: bool
    serial_number: bytes
    held_xdbg: bytes
    held_dbg: bytes

    def __init__(self, comport: str):
        self.sequence_num = 0
        comms_args = {
            "port": None,
            "baudrate": 115200,
            "bytesize": serial.EIGHTBITS,
            "parity": serial.PARITY_NONE,
            "stopbits": serial.STOPBITS_ONE,
        }
        super().__init__(**comms_args)
        self.port = comport
        self.debug_prints = False
        self.sequence_num = 0
        self.serial_number = b""
        self.redact_sn = True
        self.held_xdbg = b""
        self.held_dbg = b""

    def __enter__(self):
        self.sequence_num = 0
        return super().__enter__()

    def __exit__(self, type, value, traceback):
        return super().__exit__(type, value, traceback)

    @staticmethod
    def crc16(data: bytes):
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
        overhead_len = 14
        start = 0x03AA

        bmsg = bytes.fromhex(msg)
        msg_len = len(bmsg) - overhead_len
        bsequence = struct.pack("<I", self.sequence_num)
        bmsg_seq = bmsg[:2] + bsequence + bmsg[6:]
        headmsg = struct.pack("<HH", start, msg_len) + bmsg_seq
        crc_val = R3PComms.crc16(headmsg)
        out = headmsg + struct.pack("<H", crc_val)
        if self.debug_prints:
            print(f">>> {out.hex()}")
        ret = self.write(out)
        self.sequence_num += 1
        return ret

    def rx(self) -> bytes:
        header_len = 4
        base_len = 20

        header = self.read(header_len)
        preamble, var_len = struct.unpack("<HH", header)
        payload = self.read(base_len + var_len - header_len - 2)
        crc = self.read(2)
        full_message = header + payload + crc
        if R3PComms.crc16(full_message) == 0:
            if self.debug_prints:
                self.debug_print(full_message)
        else:
            # TODO: gracefully handle this
            raise RuntimeError("CRC check fail")
        return header + payload

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

    def segmenter(self, source: bytes) -> list[dict]:
        offset = 0
        ssize = len(source)
        result = []
        while offset < ssize:
            seg_type, seg_len = struct.unpack_from("<HB", source, offset=offset)
            seg_data = source[offset + 3 : offset + 3 + seg_len]
            offset += 3 + seg_len
            if seg_type == 3:
                seg_val = struct.unpack("<I", seg_data)[0]
                name = "Design Capacity"
                unit = "Ah"
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
                        self.debug_print(self.held_dbg, xord=True)
                        self.held_xdbg = b""
                if self.redact_sn:
                    seg_val = "REDACTED"
                    seg_data = bytes.fromhex("ff") * len(self.serial_number)
                else:
                    seg_val = seg_val.decode()
                name = "serial"
                unit = ""
            elif seg_type == 23:
                seg_val = struct.unpack("<HH", seg_data)
                seg_val = tuple([x / 60 for x in seg_val])
                name = "Time left?"
                unit = "Hr?"
            else:
                seg_val = struct.unpack("f", seg_data)[0]
                name = "unknown"
                unit = "?"
            result.append(
                {
                    "name": name,
                    "type": seg_type,
                    "data": "0x" + seg_data.hex(),
                    "value": seg_val,
                    "unit": unit,
                }
            )
        return result

    def query(self, msg: str) -> bytes:
        self.tx(msg)
        return self.rx()

    def get_serial(self):
        serial_answer_offset = 19
        answer = self.query("f40d00000000ffff2202010166031600")
        serial_result = self.segmenter(answer[serial_answer_offset:])
        return serial_result[0]["value"]

    def get_metrics(self):
        metrics_answer_offset = 22
        answer = self.query("de2d00000000ffff220201016602")
        xanswer = R3PComms.xorit(answer)
        if self.debug_prints:
            self.debug_print(xanswer, xord=True)
        metrics_result = self.segmenter(xanswer[metrics_answer_offset:])
        metrics_result.append(
            {
                "name": "preamble",
                "data": xanswer[:metrics_answer_offset].hex(),
                "value": 0,
                "unit": "",
            }
        )
        return metrics_result

    def debug_print(self, data: bytes, xord: bool = False):
        if xord:
            prompt = "<x< "
        else:
            prompt = "<<< "

        if self.redact_sn:
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
