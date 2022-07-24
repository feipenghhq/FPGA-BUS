# ------------------------------------------------------------------------------------------------
# Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
# Author: Heqing Huang
#
# Date Created: 07/04/2022
# ------------------------------------------------------------------------------------------------
# Avalon Standard Bus
# ------------------------------------------------------------------------------------------------
# Host Driver
# ------------------------------------------------------------------------------------------------

from collections import deque
import cocotb
from AvalonSPacket import AvalonSPacket

class AvalonSDriver():

    def __init__(self, port):
        self.port = port
        self.queue = deque()
        self.data = {}

    async def write(self, address, data):
        self.data[address] = data
        await self.port.write(address, data)
        packet = AvalonSPacket(address, 0, 1, data)
        self.queue.append(packet)
        cocotb.top._log.debug("Sending request: " + str(packet))

    async def read(self, address):
        data = await self.port.read(address)
        packet = AvalonSPacket(address, 1, 0, data)
        self.queue.append(packet)
