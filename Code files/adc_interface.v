`timescale 1ns/1ps
`include "beamformer_defines.vh"

module adc_model #(
    parameter NUM_LANES    = `NUM_LANES,
    parameter NUM_CH       = `NUM_CH_PER_LANE,
    parameter IQ_WIDTH     = `IQ_DATA_WIDTH,
    parameter SAMPLE_RATE  = 500_000_000  // 500 MSPS
) (
    input  wire                                           adc_clk,
    output wire [(NUM_LANES*NUM_CH*2*IQ_WIDTH)-1:0]      adc_data_out,
    output wire [NUM_LANES-1:0]                           adc_valid_out
);

    // DDS phase accumulators for each channel
    reg [31:0] phase_acc [NUM_LANES-1:0][NUM_CH-1:0];

    // Tuning words for test signals (frequency = tuning_word * fs / 2^32)
    // Example: Test signal at 10 MHz with fs = 500 MSPS
    // tuning_word = 10M / 500M * 2^32 ≈ 0x08000000
    localparam TUNING_WORD = 32'h08000000;

    integer lane, ch;

    always @(posedge adc_clk) begin
        // Phase accumulator: increment frequency
        for (lane = 0; lane < NUM_LANES; lane = lane + 1) begin
            for (ch = 0; ch < NUM_CH; ch = ch + 1) begin
                phase_acc[lane][ch] <= phase_acc[lane][ch] + TUNING_WORD;
            end
        end
    end

    // ========== LUT FUNCTIONS (Module-level) ==========
    function signed [IQ_WIDTH-1:0] sine_lut;
        input [7:0] idx;
        begin
            case (idx[4:0])
                5'h00: sine_lut = 16'h0000;
                5'h01: sine_lut = 16'h0c8c;
                5'h02: sine_lut = 16'h1918;
                5'h03: sine_lut = 16'h2528;
                5'h04: sine_lut = 16'h30fb;
                5'h05: sine_lut = 16'h3c56;
                5'h06: sine_lut = 16'h471c;
                5'h07: sine_lut = 16'h5133;
                5'h08: sine_lut = 16'h5a82;
                5'h09: sine_lut = 16'h62f2;
                5'h0a: sine_lut = 16'h6a6d;
                5'h0b: sine_lut = 16'h70e2;
                5'h0c: sine_lut = 16'h7641;
                5'h0d: sine_lut = 16'h7a7d;
                5'h0e: sine_lut = 16'h7d8a;
                5'h0f: sine_lut = 16'h7f61;
                default: sine_lut = 16'h7fff;
            endcase
        end
    endfunction

    function signed [IQ_WIDTH-1:0] cosine_lut;
        input [7:0] idx;
        begin
            cosine_lut = sine_lut(idx + 8'h08);  // cos = sin(θ + π/2)
        end
    endfunction

    // ========== GENERATE IQ SAMPLES FROM PHASE ==========
    genvar lane_idx, ch_idx;
    generate
        for (lane_idx = 0; lane_idx < NUM_LANES; lane_idx = lane_idx + 1) begin : GEN_LANE_ADC
            for (ch_idx = 0; ch_idx < NUM_CH; ch_idx = ch_idx + 1) begin : GEN_CH_ADC
                wire [31:0] phase;
                wire [7:0] phase_idx;
                wire signed [IQ_WIDTH-1:0] i_sample;
                wire signed [IQ_WIDTH-1:0] q_sample;

                // Get phase from accumulator
                assign phase = phase_acc[lane_idx][ch_idx];
                assign phase_idx = phase[31:24];  // Use top 8 bits as LUT index

                // Get I and Q samples from LUTs
                assign i_sample = sine_lut(phase_idx);
                assign q_sample = cosine_lut(phase_idx);

                // Pack IQ into flattened output bus
                // Format: [lane1_ch23_Q | lane1_ch23_I | ... | lane0_ch0_Q | lane0_ch0_I]
                assign adc_data_out[(lane_idx*NUM_CH*2*IQ_WIDTH) + (ch_idx*2*IQ_WIDTH) + (IQ_WIDTH-1) : 
                                    (lane_idx*NUM_CH*2*IQ_WIDTH) + (ch_idx*2*IQ_WIDTH)] = i_sample;

                assign adc_data_out[(lane_idx*NUM_CH*2*IQ_WIDTH) + (ch_idx*2*IQ_WIDTH) + (2*IQ_WIDTH-1) : 
                                    (lane_idx*NUM_CH*2*IQ_WIDTH) + (ch_idx*2*IQ_WIDTH) + IQ_WIDTH] = q_sample;
            end
        end
    endgenerate

    // Always valid in simulation
    assign adc_valid_out = {NUM_LANES{1'b1}};

endmodule
