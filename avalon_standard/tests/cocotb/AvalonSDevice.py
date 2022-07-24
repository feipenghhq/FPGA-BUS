# ------------------------------------------------------------------------------------------------
# Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
# Author: Heqing Huang
#
# Date Created: 07/04/2022
# ------------------------------------------------------------------------------------------------
# Avalon Standard Bus
# ------------------------------------------------------------------------------------------------
# Avalon Device
# ------------------------------------------------------------------------------------------------

from collections import deque
import random
import cocotb
from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly, NextTimeStep, Timer
from AvalonSPacket import AvalonSPacket

class AvalonSDevice(BusDriver):
    """Avalon Standard bus monitor."""

    _signals = ["address"]
    _optional_signals = ["readdata", "read", "write", "waitrequest",
                         "writedata", "readdatavalid", "byteenable",
                         "cs"]
    _avalon_properties = {
        "readLatency": 1,    # number of cycles
        "WaitReq": True,     # generate random waitrequest
    }


    def __init__(self, entity, name, clock, avl_properties={}, **kwargs):
        BusDriver.__init__(self, entity, name, clock, **kwargs)

        if avl_properties != {}:
            for key, value in self._avalon_properties.items():
                self._avalon_properties[key] = avl_properties.get(key, value)

        self._mem = {}

        if hasattr(self.bus, "readdatavalid"):
            self.bus.readdatavalid.setimmediatevalue(0)

        if hasattr(self.bus, "waitrequest"):
            self.bus.waitrequest.setimmediatevalue(0)

        self._coro = cocotb.fork(self._respond())

        self.recvQ = deque()
        self.sendQ = deque()

    async def _waitrequest(self):
        """Generate waitrequest randomly."""
        self.bus.waitrequest.value = 0
        if self._avalon_properties.get("WaitReq", True):
            if random.choice([True, False]):
                self.bus.waitrequest.value = 1
                await RisingEdge(self.clock)
            self.bus.waitrequest.value = 0

    async def _respond(self):
        """Coroutine to respond to the actual requests."""
        edge = RisingEdge(self.clock)
        while True:
            await edge
            cocotb.fork(self._waitrequest())

            if self.bus.read.value.integer and not self.bus.waitrequest.value.integer:
                addr = self.bus.address.value.integer
                #assert self.bus.read.value.integer # make sure read request is still asserted
                # wait for read data
                for i in range(self._avalon_properties["readLatency"]):
                    await edge
                    self.bus.readdata.value = self._mem[addr]
                    self.log.debug("[Device] Read from address 0x%x returning 0x%x", addr, self._mem[addr])
                    packet = AvalonSPacket(addr, 1, 0, self._mem[addr])
                    self.sendQ.append(packet)

            if self.bus.write.value.integer and not self.bus.waitrequest.value.integer:
                addr = self.bus.address.value.integer
                data = self.bus.writedata.value.integer
                assert self.bus.write.value.integer # make sure write request is still asserted
                self.log.debug("[Device] Write to address 0x%x -> 0x%x", addr, data)
                self._mem[addr] = data
                packet = AvalonSPacket(addr, 0, 1, data)
                self.recvQ.append(packet)
