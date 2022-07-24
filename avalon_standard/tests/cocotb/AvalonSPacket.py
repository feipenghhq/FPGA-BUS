# ------------------------------------------------------------------------------------------------
# Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
# Author: Heqing Huang
#
# Date Created: 07/04/2022
# ------------------------------------------------------------------------------------------------
# Avalon Standard Bus
# ------------------------------------------------------------------------------------------------
# Avalon Standard packet
# ------------------------------------------------------------------------------------------------

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