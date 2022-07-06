// ------------------------------------------------------------------------------------------------
// Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
// Author: Heqing Huang
//
// Date Created: 07/04/2022
// ------------------------------------------------------------------------------------------------
// Avalon Standard Bus
// ------------------------------------------------------------------------------------------------
// Testbench
// ------------------------------------------------------------------------------------------------


module tb #(
    parameter NH = 2,   // number of host
    parameter ND = 2,   // number of device
    parameter DW = 32,  // data width
    parameter AW = 32   // address width
) (
    input               clk,
    input               rst,

    // avalon bus input
    input               host0_avn_read,
    input               host0_avn_write,
    input  [AW-1:0]     host0_avn_address,
    input  [DW/8-1:0]   host0_avn_byte_enable,
    input  [DW-1:0]     host0_avn_writedata,
    output [DW-1:0]     host0_avn_readdata,
    output              host0_avn_waitrequest,

    input               host1_avn_read,
    input               host1_avn_write,
    input  [AW-1:0]     host1_avn_address,
    input  [DW/8-1:0]   host1_avn_byte_enable,
    input  [DW-1:0]     host1_avn_writedata,
    output [DW-1:0]     host1_avn_readdata,
    output              host1_avn_waitrequest,

    // avalon bus output
    output              device0_avn_read,
    output              device0_avn_write,
    output [AW-1:0]     device0_avn_address,
    output [DW/8-1:0]   device0_avn_byte_enable,
    output [DW-1:0]     device0_avn_writedata,
    input  [DW-1:0]     device0_avn_readdata,
    input               device0_avn_waitrequest,

    output              device1_avn_read,
    output              device1_avn_write,
    output [AW-1:0]     device1_avn_address,
    output [DW/8-1:0]   device1_avn_byte_enable,
    output [DW-1:0]     device1_avn_writedata,
    input  [DW-1:0]     device1_avn_readdata,
    input               device1_avn_waitrequest,

    // address range for each device
    input  [AW-1:0]     device0_address_low,
    input  [AW-1:0]     device0_address_high,
    input  [AW-1:0]     device1_address_low,
    input  [AW-1:0]     device1_address_high
);

    logic [ND-1:0][AW-1:0]     devices_address_low;
    logic [ND-1:0][AW-1:0]     devices_address_high;

    logic [NH-1:0]             hosts_avn_read;
    logic [NH-1:0]             hosts_avn_write;
    logic [NH-1:0][AW-1:0]     hosts_avn_address;
    logic [NH-1:0][DW/8-1:0]   hosts_avn_byte_enable;
    logic [NH-1:0][DW-1:0]     hosts_avn_writedata;
    logic [NH-1:0][DW-1:0]     hosts_avn_readdata;
    logic [NH-1:0]             hosts_avn_waitrequest;

    // avalon bus output
    logic [ND-1:0]             devices_avn_read;
    logic [ND-1:0]             devices_avn_write;
    logic [ND-1:0][AW-1:0]     devices_avn_address;
    logic [ND-1:0][DW/8-1:0]   devices_avn_byte_enable;
    logic [ND-1:0][DW-1:0]     devices_avn_writedata;
    logic [ND-1:0][DW-1:0]     devices_avn_readdata;
    logic [ND-1:0]             devices_avn_waitrequest;

    assign devices_address_low[0] = device0_address_low;
    assign devices_address_high[0] = device0_address_high;
    assign devices_address_low[1] = device1_address_low;
    assign devices_address_high[1] = device1_address_high;

    assign hosts_avn_read[0] = host0_avn_read;
    assign hosts_avn_write[0] = host0_avn_write;
    assign hosts_avn_address[0] = host0_avn_address;
    assign hosts_avn_byte_enable[0] = host0_avn_byte_enable;
    assign hosts_avn_writedata[0] = host0_avn_writedata;
    assign host0_avn_readdata = hosts_avn_readdata[0];
    assign host0_avn_waitrequest = hosts_avn_waitrequest[0];

    assign hosts_avn_read[1] = host1_avn_read;
    assign hosts_avn_write[1] = host1_avn_write;
    assign hosts_avn_address[1] = host1_avn_address;
    assign hosts_avn_byte_enable[1] = host1_avn_byte_enable;
    assign hosts_avn_writedata[1] = host1_avn_writedata;
    assign host1_avn_readdata = hosts_avn_readdata[1];
    assign host1_avn_waitrequest = hosts_avn_waitrequest[1];

    assign device0_avn_read = devices_avn_read[0];
    assign device0_avn_write = devices_avn_write[0];
    assign device0_avn_address = devices_avn_address[0];
    assign device0_avn_byte_enable = devices_avn_byte_enable[0];
    assign device0_avn_writedata = devices_avn_writedata[0];
    assign devices_avn_readdata[0] = device0_avn_readdata;
    assign devices_avn_waitrequest[0] = device0_avn_waitrequest;

    assign device1_avn_read = devices_avn_read[1];
    assign device1_avn_write = devices_avn_write[1];
    assign device1_avn_address = devices_avn_address[1];
    assign device1_avn_byte_enable = devices_avn_byte_enable[1];
    assign device1_avn_writedata = devices_avn_writedata[1];
    assign devices_avn_readdata[1] = device1_avn_readdata;
    assign devices_avn_waitrequest[1] = device1_avn_waitrequest;

    avalon_s_matrix #(.NH(NH),.ND(ND),.DW(DW),.AW(AW)) DUT (.*);

endmodule
