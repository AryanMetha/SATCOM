module axi_stream_output #(
    parameter DATA_WIDTH = 50  // 25-bit real + 25-bit imag
) (
    input  wire                 clk,
    input  wire                 rst_n,

    // Beamformed data input
    input  wire [DATA_WIDTH-1:0]    beam_data_i,
    input  wire                     beam_valid_i,

    // AXI-Stream master
    output wire [DATA_WIDTH-1:0]    m_axis_tdata,
    output wire                     m_axis_tvalid,
    input  wire                     m_axis_tready
);

    // Simple pass-through with handshaking
    reg [DATA_WIDTH-1:0] data_reg;
    reg valid_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data_reg <= 0;
            valid_reg <= 0;
        end else if (m_axis_tready) begin
            data_reg <= beam_data_i;
            valid_reg <= beam_valid_i;
        end
    end

    assign m_axis_tdata = data_reg;
    assign m_axis_tvalid = valid_reg;

endmodule
