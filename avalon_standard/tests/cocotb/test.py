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
import random
import os
import cocotb
from testbench import test_single_host

# ----------------------------------------------------------------

if 'size' in os.environ:
    size = int(os.environ['size'])
else:
    size = 10

@cocotb.test()
async def test_host0_device0(dut):
    await test_single_host(dut, 0x0, 0, 0, size=size)

@cocotb.test()
async def test_host0_device1(dut):
    await test_single_host(dut, 0x40000000, 0, 1, size=size)

@cocotb.test()
async def test_host1_device0(dut):
    await test_single_host(dut, 0x0, 1, 0, size=size)

@cocotb.test()
async def test_host1_device1(dut):
    await test_single_host(dut, 0x40000000, 1, 1, size=size)

@cocotb.test()
async def test_host0_device0_wait(dut):
    await test_single_host(dut, 0x0, 0, 0, WaitReq=True, size=size)

@cocotb.test()
async def test_host0_device1_wait(dut):
    await test_single_host(dut, 0x40000000, 0, 1, WaitReq=True, size=size)

@cocotb.test()
async def test_host1_device0_wait(dut):
    await test_single_host(dut, 0x0, 1, 0, WaitReq=True, size=size)

@cocotb.test()
async def test_host1_device1_wait(dut):
    await test_single_host(dut, 0x40000000, 1, 1, WaitReq=True, size=size)

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

#@cocotb.test()
async def test_host_to_diff_device_0(dut):
    """ Test multiple host to different device at the same time
        host 0 -> device 0
        host 1 -> device 1
    """
    env = Env(dut, 2, 2)
    await env.clock_gen()
    await env.reset_gen()
    base0 = 0x0
    base1 = 0x40000000
    await test_host_util_1(dut, env.drivers[0], env.drivers[1], base0, base1, env.devices[0], env.devices[1])

#@cocotb.test()
async def test_host_to_diff_device_1(dut):
    """ Test multiple host to different device at the same time
        host 0 -> device 1
        host 1 -> device 0
    """
    env = Env(dut, 2, 2)
    await env.clock_gen()
    await env.reset_gen()
    base0 = 0x40000000
    base1 = 0x0
    await test_host_util_1(dut, env.drivers[0], env.drivers[1], base0, base1, env.devices[1], env.devices[0])

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

#@cocotb.test()
async def test_host_to_same_device_0(dut):
    """ Test multiple host to same device at the same time
        host 0 -> device 0
        host 1 -> device 0
    """
    env = Env(dut, 2, 2)
    await env.clock_gen()
    await env.reset_gen()
    base = 0
    await test_host_util_2(dut, env.drivers[0], env.drivers[1], base, env.devices[0])
    await Timer(100, units="ns")

#@cocotb.test()
async def test_host_to_same_device_1(dut):
    """ Test multiple host to same device at the same time
        host 0 -> device 1
        host 1 -> device 1
    """
    env = Env(dut, 2, 2)
    await env.clock_gen()
    await env.reset_gen()
    base = 0x40000000
    await test_host_util_2(dut, env.drivers[0], env.drivers[1], base, env.devices[1])
    await Timer(100, units="ns")
