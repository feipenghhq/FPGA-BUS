// ------------------------------------------------------------------------------------------------
// Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
// Author: Heqing Huang
//
// Date Created: 07/04/2022
// ------------------------------------------------------------------------------------------------
// Avalon StaNHard Bus
// ------------------------------------------------------------------------------------------------
// Avalon bus arbiter aNH router
// ------------------------------------------------------------------------------------------------

module avalon_s_arbiter #(
    parameter NH = 2,   // number of host
    parameter DW = 32,  // data width
    parameter AW = 32   // address width
) (
    input                       clk,
    input                       rst,

    // avalon bus input
    input  [NH-1:0]             hosts_avn_read,
    input  [NH-1:0]             hosts_avn_write,
    input  [NH-1:0][AW-1:0]     hosts_avn_address,
    input  [NH-1:0][DW/8-1:0]   hosts_avn_byte_enable,
    input  [NH-1:0][DW-1:0]     hosts_avn_writedata,
    output [NH-1:0][DW-1:0]     hosts_avn_readdata,
    output [NH-1:0]             hosts_avn_waitrequest,

    // avalon bus output
    output                      device_avn_read,
    output                      device_avn_write,
    output [AW-1:0]             device_avn_address,
    output [DW/8-1:0]           device_avn_byte_enable,
    output [DW-1:0]             device_avn_writedata,
    input  [DW-1:0]             device_avn_readdata,
    input                       device_avn_waitrequest
);


    logic [NH-1:0]      hosts_grant;
    logic [NH-1:0]      hosts_request;

    assign hosts_grant = hosts_avn_read | hosts_avn_write;

    genvar i;
    generate
        for (i = 0; i < NH; i++) begin
            // connect output to input
            assign hosts_avn_readdata[i] = device_avn_readdata;
            assign hosts_avn_waitrequest[i] = device_avn_waitrequest;

            assign device_avn_read = |(hosts_grant & hosts_avn_read);
            assign device_avn_write = |(hosts_grant & hosts_avn_write);
            assign device_avn_address = device_avn_address | (hosts_avn_address[i] & {AW{hosts_grant[i]}});
            assign device_avn_writedata = device_avn_writedata | (hosts_avn_writedata[i] & {AW{hosts_grant[i]}});
            assign device_avn_byte_enable = device_avn_byte_enable | (hosts_avn_byte_enable[i] & {(DW/8){hosts_grant[i]}});
        end

    endgenerate

    bus_arbiter #(.WIDTH(NH))
    u_bus_arbiter (
        .req    (hosts_request),
        .base   ('1),
        .grant  (hosts_grant)
    );

endmodule