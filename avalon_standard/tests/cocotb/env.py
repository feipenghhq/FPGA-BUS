# ------------------------------------------------------------------------------------------------
# Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
# Author: Heqing Huang
#
# Date Created: 07/04/2022
# ------------------------------------------------------------------------------------------------
# Avalon Standard Bus
# ------------------------------------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------------------------------------

from collections import deque

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb_bus.drivers.avalon import AvalonMaster, AvalonMemory
from AvalonSMonitor import AvalonSMonitor, AvalonSPacket
from hostDriver import hostDriver

DEVICE_0_ADDR_LO = 0x00000000
DEVICE_0_ADDR_HI = 0x3FFFFFFF
DEVICE_1_ADDR_LO = 0x40000000
DEVICE_1_ADDR_HI = 0x7FFFFFFF

class Env:

    def __init__(self, dut):
        self.dut = dut
        self.host0 = AvalonMaster(dut, "host0_avn", dut.clk)
        self.host1 = AvalonMaster(dut, "host1_avn", dut.clk)
        self.host0_driver = hostDriver(self.host0)
        self.host1_driver = hostDriver(self.host1)
        self.device0 = AvalonMemory(dut, "device0_avn", dut.clk, readlatency_min=0, readlatency_max=0)
        self.device1 = AvalonMemory(dut, "device1_avn", dut.clk, readlatency_min=0, readlatency_max=0)
        self.device0_mon = AvalonSMonitor(dut, "device0_avn", dut.clk)
        self.device1_mon = AvalonSMonitor(dut, "device1_avn", dut.clk)
        self.config_address()

    def config_address(self):
        self.dut.device0_address_low.value = DEVICE_0_ADDR_LO
        self.dut.device0_address_high.value = DEVICE_0_ADDR_HI
        self.dut.device1_address_low.value = DEVICE_1_ADDR_LO
        self.dut.device1_address_high.value = DEVICE_1_ADDR_HI

    async def clock_gen(self, period=10):
        """ Generate Clock """
        c = Clock(self.dut.clk, period, units="ns")
        await cocotb.start(c.start())

    async def reset_gen(self, time=100):
        """ Reset the design """
        self.dut.rst.value = 1
        await Timer(time, units="ns")
        await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)
        self.dut._log.info(f"Reset Done!")

