// ------------------------------------------------------------------------------------------------
// Copyright 2022 by Heqing Huang (feipenghhq@gamil.com)
// Author: Heqing Huang
//
// Date Created: 07/04/2022
// ------------------------------------------------------------------------------------------------
// FPGA-BUS
// ------------------------------------------------------------------------------------------------
// Fixed priority arbiter
// ------------------------------------------------------------------------------------------------

module bus_arbiter #(
    parameter WIDTH = 16
) (
    input [WIDTH-1:0]       req,
    input [WIDTH-1:0]       base,   // the base is a one-hot encoding indicating the request that has highest priority
    output [WIDTH-1:0]      grant
);

    wire [WIDTH*2-1:0] double_req;
    wire [WIDTH*2-1:0] double_grant;

    assign double_req = {req, req};
    assign double_grant = double_req & (~double_req + {{WIDTH{1'b0}}, base});
    assign grant = double_grant[WIDTH-1:0] | double_grant[WIDTH*2-1:WIDTH];

endmodule