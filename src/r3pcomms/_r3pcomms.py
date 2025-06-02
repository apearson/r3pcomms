#!/usr/bin/env python3

import serial
import struct


class R3PComms(serial.Serial):
    """
    River 3 Plus comms from scratch via USB CDC (ACM)
    """

    base_len = 20
    header_len = 4
    header = 0x03AA
    overhead_len = 14

    def __init__(self, comport: str):
        comms_args = {
            "port": None,
            "baudrate": 115200,
            "bytesize": serial.EIGHTBITS,
            "parity": serial.PARITY_NONE,
            "stopbits": serial.STOPBITS_ONE,
        }
        super().__init__(**comms_args)
        self.port = comport

    def __enter__(self):
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

    def tx(self, msg: str):
        bmsg = bytes.fromhex(msg)
        msg_len = len(bmsg) - self.overhead_len
        headmsg = struct.pack("<HH", self.header, msg_len) + bmsg
        crc_val = R3PComms.crc16(headmsg)
        out = headmsg + struct.pack("<H", crc_val)
        # print(f'>>> {bmsg.hex()}')
        return self.write(out)

    def rx(self):
        header = self.read(self.header_len)
        preamble, var_len = struct.unpack("<HH", header)
        payload = self.read(self.base_len + var_len - self.header_len - 2)
        crc = self.read(2)
        if R3PComms.crc16(header + payload + crc) == 0:
            pass
            # print(f'<<< {payload.hex()}')
        else:
            # TODO: gracefully handle this
            raise RuntimeError("CRC check fail")
        return payload

    def query(self, msg: str):
        self.tx(msg)
        return self.rx()

    def get_serial(self):
        serial_payload = self.query("f40d00000000ffff2202010166031600")
        rheader, serial = struct.unpack("18s16s", serial_payload)
        return serial.decode()
