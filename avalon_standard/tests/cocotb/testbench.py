# ------------------------------------------------------------------------------------------------
# Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
# Author: Heqing Huang
#
# Date Created: 07/04/2022
# Version: 1.0: 07/24/2022
# ------------------------------------------------------------------------------------------------
# Avalon Standard Bus
# ------------------------------------------------------------------------------------------------
# Version: 1.0: basic test function
# ------------------------------------------------------------------------------------------------

from collections import deque
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from env import Env

# ----------------------------------------------------------------

async def test_single_host(dut, base, hid, did, WaitReq=False, size=10):
    """ Test single host to single device """

    env = Env(dut, 2, 2, WaitReq=WaitReq)
    host = env.drivers[hid]
    device = env.devices[did]

    start = 0x0
    end = 0x3FFFFFFF
    delta = int((end - start) / size)

    await env.clock_gen()
    await env.reset_gen()
    await host.write(base+start,    0xbeefcafe)
    await host.write(base+end,      0xcafebeef)

    for i in range(size):
        data = random.randint(0, 1024)
        addr = start + delta * i
        await host.write(base+addr, data)

    await host.read(base+0x0)
    await host.read(base+0x3FFFFFFF)
    for i in range(size):
        addr = start + delta * i
        await host.read(base+addr)

    await Timer(100, units="ns")

    # check result
    for i in range(size):
        host_pkt = host.queue.popleft()
        device_pkt = device.recvQ.popleft()
        error_msg = f"\nID: {i+1} \nhost:   {host_pkt} \ndevice: {device_pkt}"
        assert host_pkt == device_pkt, error_msg

# ----------------------------------------------------------------

