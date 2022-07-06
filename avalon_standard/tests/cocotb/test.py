# ------------------------------------------------------------------------------------------------
# Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
# Author: Heqing Huang
#
# Date Created: 07/04/2022
# ------------------------------------------------------------------------------------------------
# Avalon Standard Bus
# ------------------------------------------------------------------------------------------------
# Direct test bus matrix
# ------------------------------------------------------------------------------------------------

from collections import deque

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from env import Env

# ----------------------------------------------------------------

async def test_host_util(dut, base, host, mon):
    """ Test single host to single device """
    await host.write(base+0x10000000, 0xbeefcafe)
    await host.write(base+0x20000000, 0xdeadbeef)
    await host.write(base+0x0, 0x11223344)
    await host.write(base+0x3FFFFFFF, 0x55667788)
    await host.read(base+0x10000000)
    await host.read(base+0x20000000)
    await host.read(base+0x0)
    await host.read(base+0x3FFFFFFF)
    await Timer(100, units="ns")
    # check result
    for i in range(4):
        host_pkt = host.queue.popleft()
        device_pkt = mon.recvQ.popleft()
        error_msg = f"\nID: {i+1} \nhost:   {host_pkt} \ndevice: {device_pkt}"
        assert host_pkt == device_pkt, error_msg

@cocotb.test()
async def test_host0_device0(dut):
    env = Env(dut)
    await env.clock_gen()
    await env.reset_gen()
    base = 0x0
    await test_host_util(dut, base, env.host0_driver, env.device0_mon)

@cocotb.test()
async def test_host0_device1(dut):
    env = Env(dut)
    await env.clock_gen()
    await env.reset_gen()
    base = 0x40000000
    await test_host_util(dut, base, env.host0_driver, env.device1_mon)

@cocotb.test()
async def test_host1_device0(dut):
    env = Env(dut)
    await env.clock_gen()
    await env.reset_gen()
    base = 0x0
    await test_host_util(dut, base, env.host1_driver, env.device0_mon)

@cocotb.test()
async def test_host1_device1(dut):
    env = Env(dut)
    await env.clock_gen()
    await env.reset_gen()
    base = 0x40000000
    await test_host_util(dut, base, env.host1_driver, env.device1_mon)

# ----------------------------------------------------------------

async def test_host_util_1(dut, host0, host1, base0, base1, mon0, mon1):
    """ Test multiple host to different device at the same time """
    cocotb.start_soon(host0.write(base0+0x10000000, 0xbeefcafe))
    cocotb.start_soon(host1.write(base1+0x10000000, 0xdeadbeef))
    await Timer(20, units="ns")
    cocotb.start_soon(host0.write(base0+0x20000000, 0x12345678))
    cocotb.start_soon(host1.write(base1+0x20000000, 0x87654321))
    await Timer(20, units="ns")
    cocotb.start_soon(host0.write(base0+0x00000000, 0x11111111))
    cocotb.start_soon(host1.write(base1+0x00000000, 0x22222222))
    await Timer(20, units="ns")
    cocotb.start_soon(host0.write(base0+0x3fffffff, 0x33333333))
    cocotb.start_soon(host1.write(base1+0x3fffffff, 0x55555555))
    await Timer(100, units="ns")
    # check result
    for i in range(4):
        host_pkt0 = host0.queue.popleft()
        device_pkt0 = mon0.recvQ.popleft()
        error_msg = f"\nID: {i+1} \nhost:   {host_pkt0} \ndevice: {device_pkt0}"
        assert host_pkt0 == device_pkt0, error_msg
        host_pkt1 = host1.queue.popleft()
        device_pkt1 = mon1.recvQ.popleft()
        error_msg = f"\nID: {i+1} \nhost:   {host_pkt1} \ndevice: {device_pkt1}"
        assert host_pkt1 == device_pkt1, error_msg

@cocotb.test()
async def test_host_to_diff_device_0(dut):
    """ Test multiple host to different device at the same time
        host 0 -> device 0
        host 1 -> device 1
    """
    env = Env(dut)
    await env.clock_gen()
    await env.reset_gen()
    base0 = 0x0
    base1 = 0x40000000
    await test_host_util_1(dut, env.host0_driver, env.host1_driver, base0, base1, env.device0_mon, env.device1_mon)

@cocotb.test()
async def test_host_to_diff_device_1(dut):
    """ Test multiple host to different device at the same time
        host 0 -> device 1
        host 1 -> device 0
    """
    env = Env(dut)
    await env.clock_gen()
    await env.reset_gen()
    base0 = 0x40000000
    base1 = 0x0
    await test_host_util_1(dut, env.host0_driver, env.host1_driver, base0, base1, env.device1_mon, env.device0_mon)

# ----------------------------------------------------------------

async def test_host_util_2(dut, host0, host1, base, mon):
    """ Test multiple host to same device at the same time """
    cocotb.start_soon(host0.write(base+0x0, 0xbeefcafe))    # host 0 has priority
    cocotb.start_soon(host1.write(base+0x4, 0xdeadbeef))
    await Timer(100, units="ns")
    cocotb.start_soon(host0.write(base+0x10, 0x12345678))    # host 0 has priority
    cocotb.start_soon(host1.write(base+0x14, 0x87654321))
    await Timer(100, units="ns")
    # check result
    for i in range(2):
        host_pkt0 = host0.queue.popleft()
        device_pkt0 = mon.recvQ.popleft()
        error_msg = f"\nID: {i+1} \nhost:   {host_pkt0} \ndevice: {device_pkt0}"
        assert host_pkt0 == device_pkt0, error_msg
        host_pkt1 = host1.queue.popleft()
        device_pkt1 = mon.recvQ.popleft()
        error_msg = f"\nID: {i+1} \nhost:   {host_pkt1} \ndevice: {device_pkt1}"
        assert host_pkt1 == device_pkt1, error_msg

@cocotb.test()
async def test_host_to_same_device_0(dut):
    """ Test multiple host to same device at the same time
        host 0 -> device 0
        host 1 -> device 0
    """
    env = Env(dut)
    await env.clock_gen()
    await env.reset_gen()
    base = 0
    await test_host_util_2(dut, env.host0_driver, env.host1_driver, base, env.device0_mon)
    await Timer(100, units="ns")

@cocotb.test()
async def test_host_to_same_device_1(dut):
    """ Test multiple host to same device at the same time
        host 0 -> device 1
        host 1 -> device 1
    """
    env = Env(dut)
    await env.clock_gen()
    await env.reset_gen()
    base = 0x40000000
    await test_host_util_2(dut, env.host0_driver, env.host1_driver, base, env.device1_mon)
    await Timer(100, units="ns")
