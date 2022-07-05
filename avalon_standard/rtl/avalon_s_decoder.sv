// ------------------------------------------------------------------------------------------------
// Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
// Author: Heqing Huang
//
// Date Created: 07/04/2022
// ------------------------------------------------------------------------------------------------
// Avalon Standard Bus
// ------------------------------------------------------------------------------------------------
// Avalon bus decoder and router
// ------------------------------------------------------------------------------------------------


module avalon_s_decoder #(
    parameter ND = 2,   // number of device
    parameter DW = 32,  // data width
    parameter AW = 32   // address width
) (
    input                       clk,
    input                       rst,

    // avalon bus input
    input                       host_avn_read,
    input                       host_avn_write,
    input  [AW-1:0]             host_avn_address,
    input  [DW/8-1:0]           host_avn_byte_enable,
    input  [DW-1:0]             host_avn_writedata,
    output [DW-1:0]             host_avn_readdata,
    output                      host_avn_waitrequest,

    // avalon bus output
    output [ND-1:0]             devices_avn_read,
    output [ND-1:0]             devices_avn_write,
    output [ND-1:0][AW-1:0]     devices_avn_address,
    output [ND-1:0][DW/8-1:0]   devices_avn_byte_enable,
    output [ND-1:0][DW-1:0]     devices_avn_writedata,
    input  [ND-1:0][DW-1:0]     devices_avn_readdata,
    input  [ND-1:0]             devices_avn_waitrequest,

    // address range for each device
    input  [ND-1:0][AW-1:0]     devices_address_low,
    input  [ND-1:0][AW-1:0]     devices_address_high
);

    logic [ND-1:0]  devices_hit;
    reg   [ND-1:0]  prev_devices_hit;


    genvar i;
    generate
        for (i = 0; i < ND; i++) begin
            // check which device hit
            assign devices_hit[i] = (host_avn_address >= devices_address_low[i]) & (host_avn_address <= devices_address_high[i]);

            // connect output to input
            assign devices_avn_write[i] = devices_hit[i] & host_avn_write;
            assign devices_avn_read[i] = devices_hit[i] & host_avn_read;
            assign devices_avn_address[i] = host_avn_address;
            assign devices_avn_byte_enable[i] = host_avn_byte_enable;
            assign devices_avn_writedata[i] = host_avn_writedata;

            assign host_avn_readdata = host_avn_readdata | (devices_avn_readdata[i] & {DW{prev_devices_hit[i]}});
        end
    endgenerate

    always @(posedge clk) begin
        prev_devices_hit <= devices_hit;
    end

    assign host_avn_waitrequest = | (devices_avn_waitrequest & devices_hit);


endmodule