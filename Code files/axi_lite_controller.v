module axi_lite_controller #(
    parameter ADDR_WIDTH = 12,
    parameter DATA_WIDTH = 32
) (
    input  wire                     axi_clk,
    input  wire                     axi_rst_n,

    // AXI-Lite Write Address Channel
    input  wire [ADDR_WIDTH-1:0]    awaddr,
    input  wire                     awvalid,
    output wire                     awready,

    // AXI-Lite Write Data Channel
    input  wire [DATA_WIDTH-1:0]    wdata,
    input  wire                     wvalid,
    output wire                     wready,

    // AXI-Lite Write Response Channel
    output wire                     bvalid,
    input  wire                     bready,

    // Internal coefficient write signals
    output wire [7:0]               coeff_addr,
    output wire [31:0]              coeff_data,
    output wire                     coeff_we
);

    // Simplified AXI-Lite slave
    // In practice, expand with proper burst support, error handling, etc.

    reg [ADDR_WIDTH-1:0] addr_reg;
    reg addr_accepted;
    reg data_accepted;

    // Write address channel
    assign awready = !addr_accepted;
    always @(posedge axi_clk or negedge axi_rst_n) begin
        if (!axi_rst_n) begin
            addr_reg <= 0;
            addr_accepted <= 0;
        end else if (awvalid && awready) begin
            addr_reg <= awaddr;
            addr_accepted <= 1;
        end else if (bvalid && bready) begin
            addr_accepted <= 0;
        end
    end

    // Write data channel
    assign wready = !data_accepted;
    always @(posedge axi_clk or negedge axi_rst_n) begin
        if (!axi_rst_n) begin
            data_accepted <= 0;
        end else if (wvalid && wready) begin
            data_accepted <= 1;
        end else if (bvalid && bready) begin
            data_accepted <= 0;
        end
    end

    // Write response channel
    assign bvalid = addr_accepted && data_accepted;

    // Coefficient write
    assign coeff_addr = addr_reg[7:0];
    assign coeff_data = wdata;
    assign coeff_we = wvalid && wready;

endmodule
