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

    def rx(self):
        header_len = 4
        base_len = 20

        header = self.read(header_len)
        preamble, var_len = struct.unpack("<HH", header)
        payload = self.read(base_len + var_len - header_len - 2)
        crc = self.read(2)
        if R3PComms.crc16(header + payload + crc) == 0:
            if self.debug_prints:
                full_message = header + payload + crc
                print(f"<<< {full_message.hex()}")
            else:
                pass
        else:
            # TODO: gracefully handle this
            raise RuntimeError("CRC check fail")
        return payload

    @staticmethod
    def decode(payload: bytes) -> bytes:
        not_obfuscated = payload[:14]
        (sequence_num,) = struct.unpack("<I", not_obfuscated[2:6])
        deobfuscated = bytes([xor(x, sequence_num) & 0xFF for x in payload[14:]])
        return not_obfuscated + deobfuscated

    def segmenter(self, source: bytes) -> list[dict]:
        offset = 0
        ssize = len(source)
        result = []
        while offset < ssize:
            seg_type, seg_len = struct.unpack_from("<HB", source, offset=offset)
            seg_data = source[offset + 3 : offset + 3 + seg_len]
            offset += 3 + seg_len
            if seg_type == 4:
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
                seg_val = struct.unpack(f"{seg_len}s", seg_data)[0].decode()
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

    def query(self, msg: str):
        self.tx(msg)
        return self.rx()

    def get_serial(self):
        serial_payload = self.query("f40d00000000ffff2202010166031600")
        serial_result = self.segmenter(serial_payload[15:])
        return serial_result[0]["value"]

    def get_metrics(self):
        serial_payload = self.query("de2d00000000ffff220201016602")
        decoded_payload = R3PComms.decode(serial_payload)
        if self.debug_prints:
            print(f"<d< {decoded_payload.hex()}")
        metrics_result = self.segmenter(decoded_payload[18:])
        metrics_result.append(
            {
                "name": "preamble",
                "data": decoded_payload[:18].hex(),
                "value": 0,
                "unit": "",
            }
        )
        return metrics_result
