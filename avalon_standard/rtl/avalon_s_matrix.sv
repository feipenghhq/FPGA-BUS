// ------------------------------------------------------------------------------------------------
// Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
// Author: Heqing Huang
//
// Date Created: 07/04/2022
// ------------------------------------------------------------------------------------------------
// Avalon Standard Bus
// ------------------------------------------------------------------------------------------------
// Avalon bus matrix
// ------------------------------------------------------------------------------------------------


module avalon_s_matrix #(
    parameter NH = 2,   // number of host
    parameter ND = 2,   // number of device
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

    logic [NH-1:0][ND-1:0]             decoder_avn_read;
    logic [NH-1:0][ND-1:0]             decoder_avn_write;
    logic [NH-1:0][ND-1:0][AW-1:0]     decoder_avn_address;
    logic [NH-1:0][ND-1:0][DW/8-1:0]   decoder_avn_byte_enable;
    logic [NH-1:0][ND-1:0][DW-1:0]     decoder_avn_writedata;
    logic [NH-1:0][ND-1:0][DW-1:0]     decoder_avn_readdata;
    logic [NH-1:0][ND-1:0]             decoder_avn_waitrequest;

    logic [ND-1:0][NH-1:0]             arbiter_avn_read;
    logic [ND-1:0][NH-1:0]             arbiter_avn_write;
    logic [ND-1:0][NH-1:0][AW-1:0]     arbiter_avn_address;
    logic [ND-1:0][NH-1:0][DW/8-1:0]   arbiter_avn_byte_enable;
    logic [ND-1:0][NH-1:0][DW-1:0]     arbiter_avn_writedata;
    logic [ND-1:0][NH-1:0][DW-1:0]     arbiter_avn_readdata;
    logic [ND-1:0][NH-1:0]             arbiter_avn_waitrequest;

    genvar i, j;
    generate
        for (i = 0; i < ND; i++) begin  // device
            for (j = 0; j < NH; j++) begin // host
                assign arbiter_avn_read[i][j]         = decoder_avn_read[j][i];
                assign arbiter_avn_write[i][j]        = decoder_avn_write[j][i];
                assign arbiter_avn_address[i][j]      = decoder_avn_address[j][i];
                assign arbiter_avn_byte_enable[i][j]  = decoder_avn_byte_enable[j][i];
                assign arbiter_avn_writedata[i][j]    = decoder_avn_writedata[j][i];
                assign arbiter_avn_readdata[i][j]     = decoder_avn_readdata[j][i];
                assign arbiter_avn_waitrequest[i][j]  = decoder_avn_waitrequest[j][i];
            end
        end
    endgenerate

    genvar h;
    generate
        for (h = 0; h < NH; h++) begin: host_decode
            avalon_s_decoder #(.ND(ND), .DW(DW), .AW (AW))
            u_avalon_s_decoder (
                .clk                        (clk),
                .rst                        (rst),
                .host_avn_read              (hosts_avn_read[h]),
                .host_avn_write             (hosts_avn_write[h]),
                .host_avn_address           (hosts_avn_address[h]),
                .host_avn_byte_enable       (hosts_avn_byte_enable[h]),
                .host_avn_writedata         (hosts_avn_writedata[h]),
                .host_avn_readdata          (hosts_avn_readdata[h]),
                .host_avn_waitrequest       (hosts_avn_waitrequest[h]),
                .devices_avn_read           (decoder_avn_read[h]),
                .devices_avn_write          (decoder_avn_write[h]),
                .devices_avn_address        (decoder_avn_address[h]),
                .devices_avn_byte_enable    (decoder_avn_byte_enable[h]),
                .devices_avn_writedata      (decoder_avn_writedata[h]),
                .devices_avn_readdata       (decoder_avn_readdata[h]),
                .devices_avn_waitrequest    (decoder_avn_waitrequest[h]),
                .devices_address_low        (devices_address_low),
                .devices_address_high       (devices_address_high)
            );

    end
    endgenerate

    genvar d;
    generate
        for (d = 0; d < NH; d++) begin: host_decode
            avalon_s_arbiter #(.NH(NH), .DW(DW), .AW (AW))
            avalon_s_arbiter (
                .clk                        (clk),
                .rst                        (rst),
                .hosts_avn_read             (arbiter_avn_read[h]),
                .hosts_avn_write            (arbiter_avn_write[h]),
                .hosts_avn_address          (arbiter_avn_address[h]),
                .hosts_avn_byte_enable      (arbiter_avn_byte_enable[h]),
                .hosts_avn_writedata        (arbiter_avn_writedata[h]),
                .hosts_avn_readdata         (arbiter_avn_readdata[h]),
                .hosts_avn_waitrequest      (arbiter_avn_waitrequest[h]),
                .device_avn_read            (devices_avn_read[h]),
                .device_avn_write           (devices_avn_write[h]),
                .device_avn_address         (devices_avn_address[h]),
                .device_avn_byte_enable     (devices_avn_byte_enable[h]),
                .device_avn_writedata       (devices_avn_writedata[h]),
                .device_avn_readdata        (devices_avn_readdata[h]),
                .device_avn_waitrequest     (devices_avn_waitrequest[h])
            );
    end
    endgenerate

endmodule