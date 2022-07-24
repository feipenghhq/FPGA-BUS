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

    // ------------------------------
    // Sginal Declaration
    // ------------------------------

    reg                 pending;
    reg [NH-1:0]        pending_hosts_request;

    logic [NH-1:0]      grant;
    logic [NH-1:0]      hosts_request;
    logic [NH-1:0]      arbiter_request;
    logic               host_request;

    /* verilator lint_off UNOPT */
    logic [AW-1:0]      device_avn_address_temp;
    logic [DW/8-1:0]    device_avn_byte_enable_temp;
    logic [DW-1:0]      device_avn_writedata_temp;
    /* verilator lint_off UNOPT */

    // ------------------------------
    // Main logic
    // ------------------------------

    assign hosts_request = hosts_avn_read | hosts_avn_write;
    assign host_request = |hosts_request;
    assign arbiter_request = pending ? pending_hosts_request : hosts_request;

    always @(posedge clk) begin
        if (rst) pending <= 0;
        else begin
            if (!pending && host_request && device_avn_waitrequest) pending <= 1;
            else if (pending && !device_avn_waitrequest) pending <= 0;
        end
    end

    always @(posedge clk) begin
        if (!pending) pending_hosts_request <= hosts_request;
    end

    assign device_avn_address = device_avn_address_temp;
    assign device_avn_byte_enable = device_avn_byte_enable_temp;
    assign device_avn_writedata = device_avn_writedata_temp;
    assign device_avn_read = |(grant & hosts_avn_read);
    assign device_avn_write = |(grant & hosts_avn_write);

    genvar i;
    generate
        for (i = 0; i < NH; i++) begin: d2h
            // connect output to input
            assign hosts_avn_readdata[i] = device_avn_readdata;
            assign hosts_avn_waitrequest[i] = device_avn_waitrequest | ~grant[i];
        end
    endgenerate

    integer j;
    always @* begin
        device_avn_address_temp = 0;
        device_avn_writedata_temp = 0;
        device_avn_byte_enable_temp = 0;
        for (j = 0; j < NH; j++) begin
            device_avn_address_temp = device_avn_address_temp | (hosts_avn_address[j] & {AW{grant[j]}});
            device_avn_writedata_temp = device_avn_writedata_temp | (hosts_avn_writedata[j] & {AW{grant[j]}});
            device_avn_byte_enable_temp = device_avn_byte_enable_temp | (hosts_avn_byte_enable[j] & {(DW/8){grant[j]}});
        end
    end

    // ------------------------------
    // Module initialization
    // ------------------------------

    bus_arbiter #(.WIDTH(NH))
    u_bus_arbiter (
        .req    (arbiter_request),
        .base   (1),
        .grant  (grant)
    );

endmodule