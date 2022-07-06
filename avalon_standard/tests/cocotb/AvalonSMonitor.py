# ------------------------------------------------------------------------------------------------
# Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
# Author: Heqing Huang
#
# Date Created: 07/04/2022
# ------------------------------------------------------------------------------------------------
# Avalon Standard Bus
# ------------------------------------------------------------------------------------------------
# Bus monitor
# ------------------------------------------------------------------------------------------------

from cocotb_bus.monitors import BusMonitor
from cocotb.triggers import RisingEdge

class AvalonSPacket():

    def __init__(self, address, read, write, data):
        self.address = address
        self.read = read
        self.write = write
        self.data = data

    def __str__(self):
        return f"Address: {hex(self.address)}, Read: {self.read}, Write: {self.write}, Data: {hex(self.data)}"

    def __eq__(self, other):
        return self.address == other.address and self.read == other.read and \
               self.write == other.write and self.data == other.data

class AvalonSMonitor(BusMonitor):
    """Avalon Standard bus monitor."""

    _signals = ["address"]
    _optional_signals = ["readdata", "read", "write", "waitrequest",
                         "writedata", "readdatavalid", "byteenable",
                         "cs"]

    def __init__(self, entity, name, clock, **kwargs):
        BusMonitor.__init__(self, entity, name, clock, **kwargs)
        self.pending_read = False
        self.pending_read_packet = None

    async def _monitor_recv(self):
        """Watch the pins and reconstruct transactions."""
        while True:

            await RisingEdge(self.clock)

            # process the read data for previous read request
            if self.pending_read:
                self.pending_read_packet.data = self.bus.readdata.value
                self._recv(self.pending_read_packet)
                self.pending_read = False

            # write request
            if self.bus.write.value and not self.bus.waitrequest.value:
                packet = AvalonSPacket(self.bus.address.value, 0, 1, self.bus.writedata.value)
                self._recv(packet)

            # read request
            if self.bus.read.value and not self.bus.waitrequest.value:
                self.pending_read_packet = AvalonSPacket(self.bus.address.value, 1, 0, 0)
                self.pending_read = True
