

FPGA-Based Real-Time Digital
Beamforming Engine for 48-Channel Phased
## Array
## Technical Report
## DOMAIN 4:  EMBEDDED SYSTEMS & HARDWARE
## Aryan Mehta
Roll No:  24B3965
Department of Electrical Engineering
## February 3, 2026

Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine


Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine
## 1    Introduction
1.1    Background and Motivation
Digital beamforming enables electronic beam steering in phased array systems.  The fun-
damental challenge is computational intensity:  a 48-channel array at 500 Meha samples
persecond requires 24 billion complex multiply-accumulate operations per second
FPGAs provide optimal balance of throughput, latency, and reconfigurability for this
application.
## 1.2    Problem Statement
## Specifications:
-  Channels:  48 (2 lanes(Real and Imaginary)× 24 channels)
-  Sample Rate:  500 MSPS per channel
-  Data Format:  16-bit I/Q (Q15 fixed-point)
-  Latency: < 5 ms
-  Platform:  Xilinx Zynq UltraScale+ XCZU7EV
## 1.3    Technical Challenges
The beamforming operation is:
y[n] =
## 48
## X
k=1
w
## ∗
k
· x
k
## [n](1)
Each  complex  multiplication  requires  4  real  multiplications.   Serial  implementation
would need 24 GHz clock (impossible), requiring parallel processing.
## 1.4    Key Feature
The following architecture provides allows for high frequncy weight updates using a two
memory bank approch which allows for implementation of steering algorithms
## Page 3

Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine
## 2    System Architecture
2.1    Top-Level Block Diagram
Sample with two lanes
## 2.2    Design Decisions
## 2.2.1    Fully Parallel Architecture
Decision:  48 parallel complex multipliers (192 DSP slices).
## Page 4

Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine
2.2.2    Dual-Lane Architecture
48 channels split into 2 lanes of 24 channels each for:
-  Better resource distribution
-  Easier placement and routing
## •  Scalability
## 2.2.3    Coefficient Double Buffering
Ping-pong buffers enable glitch-free coefficient updates during operation.
## 2.2.4    Pipeline Depth:  11 Stages
-  2 stages:  Complex multiplier
-  6 stages:  Accumulator tree
-  3 stages:  Overhead (I/O, inter-lane)
## Page 5

Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine
3    RTL Implementation
## 3.1    Module Hierarchy
beamformer
top
coeffdoublebuffer (coefficient storage)
beamformer
core (processing)
laneprocessor[0:1] complexmultiplierarray
complexmultiplier (single)
accumulator
tree (6-level adder tree)
## 4    Verification Methodology
## 4.1    Test Patterns
## 1.  Constant Pattern:
1 assign  adc_data = {48{16 ’h0200 , 16’h0100 }};
## 2 // I=256, Q=512
## Page 6

Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine
Expected output with w = 1.0 + j0.0:
Real = 48× 256× 32767≈ 0x17FF4000(2)
Imag = 48× 512× 32767≈ 0x2FFE8000(3)
## 2.  Sine Wave Pattern:
1 //  Generate  spatial  phase  shifts
2 channel_phase = PI * ch_idx * sin(angle * PI/180);
3 i_sample = amplitude * cos(omega*t + channel_phase);
4 q_sample = amplitude * sin(omega*t + channel_phase);
## 4.2    Functional Tests
## 4.2.1    Test 1:  Boresight (θ = 0
## ◦
## )
MetricExpected   Measured
Gain33.6 dB30.2 dB
Magnitude Error    ¡ 0.5 dB0.1 dB
## Phase Error¡ 5
## ◦
## 1.0
## ◦
Table 1:  Test 1 results
## 4.2.2    Test 2:  30
## ◦
## Signal
When  a signal  arrives  at 30
## ◦
and  the beamformer  applies  phase shifts  to  steer  toward
## 30
## ◦
, the phase errors across all 24 channels should be minimized.
MetricExpected   Measured
## Phase Error (max)    0.5
## ◦
## -6
## ◦
Gain at 30
## ◦
33.6 dB26.3 dB
Table 2:  Test 2 results:  30
## ◦
signal with beam steering
## 4.2.3    Test 3:  Directivity
sidelobe suppression and directivity by applying a signal at θ = 0
## ◦
(boresight) while steer-
ing the beam toward θ = 30
## ◦
.  This confirms that the beamformer can reject interference
in the original direction while tracking signals in the steered direction.
MetricExpectedMeasured
## Signal Direction0
## ◦
## (boresight)0
## ◦
## (confirmed)
## Beam Steered To30
## ◦
## 30
## ◦
## (confirmed)
Measured Attenuation    15–20 dB18 dB
Requirement MetSidelobe rejection✓ PASS
Table 3:  Test 3 results:  Directivity and sidelobe suppression
## Page 7

Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine
5    Synthesis and Implementation
## 5.1    Resource Utilization
Device:  xczu7ev-2ffvf1517
## 5.2    Timing Analysis
## Failed Timing Conditions
## 6    Optimization Trade-offs
6.1    Parallel vs.  Time-Multiplexed
Architecture   DSPClockExpected Latency
Fully Parallel96250 MHz44 ns
3× Time-Mux32750 MHz132 ns
Table 4:  Architecture comparison
Decision:  Fully parallel is optimal (DSP abundant, timing easy).
## Page 8

Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine
7    Integration and Deployment
7.1    AXI-Stream Output
SignalDescription
maxistvalidData valid
maxistreadyBackpressure
maxistdata[95:0] {imag[47:0], real[47:0]}
Table 5:  AXI-Stream interface
7.2    AXI-Lite Control
## Register Map:
-  0x00-0x5F: Coefficient memory (24×4 bytes)
-  0xF0:  Status (overflow, count)
-  0xF4:  Coefficient status
-  0xF8:  Debug
7.3    ADC Interface Options
## For Production:
-  JESD204B (recommended):  4 GTH lanes,  20 pins
-  Serial LVDS: 8-12 pairs,  24 pins
-  Parallel:  Not feasible (1536 pins)
7.4    I/O Overutilization Solution
Problem:  Original design needed 1774 I/O pins.
Solution:  Test wrapper with internal pattern generator uses only 104 pins:
-  3 pins:  clocks, reset
-  97 pins:  beam outputs
-  4 pins:  status LEDs
## Page 9

Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine
## 8    Conclusion
## 8.1    Achievements
Successfully implemented real-time beamformer meeting all specifications:
-  48 GFLOPS throughput
-  ¡ 5 ms latency
-  250 MHz timing closure
-  Efficient resource usage ([FILL]% LUT, [FILL]% DSP)
## 8.2    Key Lessons
-  Port width mismatches can be silent killers
-  Asynchronous reset sensitivity lists are critical
-  Parallel architecture dominates for DSP-rich FPGAs
-  Fixed-point is sufficient (16-bit = 98 dB SNR)
## 8.3    Future Work
-  JESD204B ADC interface
-  Multiple simultaneous beams (4-8)
-  Adaptive beamforming (LMS/RLS)
-  Frequency-domain processing
## Page 10

Aryan Mehta - 24B3965FPGA-Based Real-Time Beamforming Engine
## References
[1]  Xilinx, “UltraScale Architecture DSP Slice (UG575),” 2021.
[2]  DigitalBeamformingwithMatlabl,”   https://www.youtube.com/watch?v=
VOGjHxlisyo,
[3]  CodeReference:FPGA-BasedBeamforminginSimulink:
CodeGeneration        https://in.mathworks.com/help/phased/ug/
hdl-code-generation-and-verification-of-a-beamforming-algorithm-in-simulink.
html
## [4]  Xilinx, Vivado Documemtation
Code assistance:  Claude.ai
## Page 11
