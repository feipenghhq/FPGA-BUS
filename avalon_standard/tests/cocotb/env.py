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
from AvalonSDriver import AvalonSDriver
from AvalonSPacket import AvalonSPacket
from AvalonSDevice import AvalonSDevice

default_addr_range = [
    (0x00000000, 0x3FFFFFFF),
    (0x40000000, 0x7FFFFFFF)
]

class Env:

    def __init__(self, dut, num_host, num_device, device_addr_range=default_addr_range, WaitReq=False):
        avl_properties={"WaitReq": WaitReq}
        self.dut = dut
        self.hosts = []
        self.drivers = []
        self.devices = []
        for h in range(num_host):
            host = AvalonMaster(dut, f"host{h}_avn", dut.clk)
            driver = AvalonSDriver(host)
            self.hosts.append(host)
            self.drivers.append(driver)
        for d in range(num_device):
            device = AvalonSDevice(dut, f"device{d}_avn", dut.clk, avl_properties)
            self.devices.append(device)
        self.device_addr_range = device_addr_range
        self.config_address()

    def config_address(self):
        for i in range(len(self.device_addr_range)):
            addr_range = self.device_addr_range[i]
            self.dut.device_address_low[i].value  = addr_range[0]
            self.dut.device_address_high[i].value = addr_range[1]

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
