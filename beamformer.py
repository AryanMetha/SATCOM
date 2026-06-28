#!/usr/bin/env python3
"""
Beamformer Golden Reference Generator and Results Analyzer
Provides MATLAB-style verification and analysis
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd
import sys

class BeamformerReference:
    def __init__(self, num_channels=48, spacing=0.5, sample_rate=500e6):
        """
        Initialize beamformer reference model
        
        Args:
            num_channels: Total number of array elements (48)
            spacing: Element spacing in wavelengths (0.5 for λ/2)
            sample_rate: ADC sample rate in Hz
        """
        self.num_channels = num_channels
        self.spacing = spacing  # in wavelengths
        self.sample_rate = sample_rate
        
        # Element positions (in wavelengths)
        self.positions = np.arange(num_channels) * spacing
        
    def generate_signal(self, angle_deg, freq, amplitude, num_samples):
        """
        Generate received signal from given direction
        
        Args:
            angle_deg: Arrival angle in degrees (0=boresight)
            freq: Signal frequency in Hz
            amplitude: Signal amplitude (0-1)
            num_samples: Number of time samples
            
        Returns:
            Complex array [num_channels, num_samples]
        """
        angle_rad = np.deg2rad(angle_deg)
        
        # Time vector
        t = np.arange(num_samples) / self.sample_rate
        
        # Spatial phase shifts (k*d*sin(theta))
        k = 2 * np.pi  # normalized to wavelength
        phase_shifts = k * self.positions * np.sin(angle_rad)
        
        # Generate complex signal for each channel
        signals = np.zeros((self.num_channels, num_samples), dtype=complex)
        
        omega = 2 * np.pi * freq
        base_signal = amplitude * np.exp(1j * omega * t)
        
        for ch in range(self.num_channels):
            signals[ch, :] = base_signal * np.exp(1j * phase_shifts[ch])
            
        return signals
    
    def calculate_steering_vector(self, angle_deg):
        """
        Calculate beamforming coefficients for given steering angle
        
        Args:
            angle_deg: Steering direction in degrees
            
        Returns:
            Complex steering vector [num_channels]
        """
        angle_rad = np.deg2rad(angle_deg)
        k = 2 * np.pi
        
        # Phase compensation: e^(-j*k*d*sin(theta))
        phase_shifts = -k * self.positions * np.sin(angle_rad)
        steering_vector = np.exp(1j * phase_shifts)
        
        return steering_vector
    
    def beamform(self, signals, steering_angle_deg):
        """
        Apply beamforming to received signals
        
        Args:
            signals: Complex array [num_channels, num_samples]
            steering_angle_deg: Beam steering direction
            
        Returns:
            Beamformed output [num_samples]
        """
        weights = self.calculate_steering_vector(steering_angle_deg)
        
        # Apply weights and sum
        output = np.sum(signals * weights[:, np.newaxis], axis=0)
        
        return output
    
    def calculate_array_pattern(self, steering_angle_deg, angles=None):
        """
        Calculate array pattern (beam pattern)
        
        Args:
            steering_angle_deg: Beam steering direction
            angles: Evaluation angles in degrees (default: -90 to 90)
            
        Returns:
            angles, pattern_db
        """
        if angles is None:
            angles = np.linspace(-90, 90, 181)
            
        weights = self.calculate_steering_vector(steering_angle_deg)
        pattern = np.zeros(len(angles))
        
        for i, angle in enumerate(angles):
            # Steering vector for this angle
            k = 2 * np.pi
            angle_rad = np.deg2rad(angle)
            phase_shifts = k * self.positions * np.sin(angle_rad)
            array_vector = np.exp(1j * phase_shifts)
            
            # Array response
            response = np.abs(np.sum(weights * np.conj(array_vector)))
            pattern[i] = response
            
        # Normalize and convert to dB
        pattern_db = 20 * np.log10(pattern / np.max(pattern))
        
        return angles, pattern_db


def analyze_results(csv_file='test_results.csv'):
    """Analyze and visualize testbench results"""
    
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found")
        return
    
    # Create figure with subplots
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(3, 2, figure=fig)
    
    # 1. Magnitude error over time
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(df['Sample'], df['Error_dB'], 'b-', linewidth=0.5)
    ax1.axhline(y=0.5, color='r', linestyle='--', label='±0.5 dB limit')
    ax1.axhline(y=-0.5, color='r', linestyle='--')
    ax1.set_xlabel('Sample Number')
    ax1.set_ylabel('Magnitude Error (dB)')
    ax1.set_title('Magnitude Error vs Time')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Phase error over time
    ax2 = fig.add_subplot(gs[1, :])
    ax2.plot(df['Sample'], df['Phase_Error_deg'], 'g-', linewidth=0.5)
    ax2.axhline(y=5, color='r', linestyle='--', label='±5° limit')
    ax2.axhline(y=-5, color='r', linestyle='--')
    ax2.set_xlabel('Sample Number')
    ax2.set_ylabel('Phase Error (degrees)')
    ax2.set_title('Phase Error vs Time')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Magnitude error histogram
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.hist(df['Error_dB'], bins=50, edgecolor='black', alpha=0.7)
    ax3.set_xlabel('Magnitude Error (dB)')
    ax3.set_ylabel('Count')
    ax3.set_title('Magnitude Error Distribution')
    ax3.grid(True, alpha=0.3)
    
    # 4. Phase error histogram
    ax4 = fig.add_subplot(gs[2, 1])
    ax4.hist(df['Phase_Error_deg'], bins=50, edgecolor='black', alpha=0.7)
    ax4.set_xlabel('Phase Error (degrees)')
    ax4.set_ylabel('Count')
    ax4.set_title('Phase Error Distribution')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test_results_analysis.png', dpi=300)
    print(f"Analysis plot saved to test_results_analysis.png")
    
    # Print statistics
    print("\n" + "="*60)
    print("STATISTICAL SUMMARY")
    print("="*60)
    print(f"Total samples analyzed: {len(df)}")
    print(f"\nMagnitude Error (dB):")
    print(f"  Mean:   {df['Error_dB'].mean():+.3f}")
    print(f"  Std:    {df['Error_dB'].std():.3f}")
    print(f"  Max:    {df['Error_dB'].max():+.3f}")
    print(f"  Min:    {df['Error_dB'].min():+.3f}")
    print(f"\nPhase Error (degrees):")
    print(f"  Mean:   {df['Phase_Error_deg'].mean():+.3f}")
    print(f"  Std:    {df['Phase_Error_deg'].std():.3f}")
    print(f"  Max:    {df['Phase_Error_deg'].max():+.3f}")
    print(f"  Min:    {df['Phase_Error_deg'].min():+.3f}")
    print("="*60 + "\n")


def plot_beam_patterns():
    """Plot theoretical beam patterns for different steering angles"""
    
    bf = BeamformerReference(num_channels=48, spacing=0.5)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Polar plot
    steering_angles = [0, 15, 30, 45]
    
    for steer_angle in steering_angles:
        angles, pattern_db = bf.calculate_array_pattern(steer_angle)
        angles_rad = np.deg2rad(angles)
        
        # Polar plot
        ax1 = plt.subplot(1, 2, 1, projection='polar')
        ax1.plot(angles_rad, pattern_db + 40, label=f'Steer={steer_angle}°')
        
    ax1.set_theta_zero_location('N')
    ax1.set_theta_direction(-1)
    ax1.set_ylim([0, 40])
    ax1.set_title('Beam Patterns (Polar)')
    ax1.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax1.grid(True)
    
    # Rectangular plot
    ax2 = plt.subplot(1, 2, 2)
    for steer_angle in steering_angles:
        angles, pattern_db = bf.calculate_array_pattern(steer_angle)
        ax2.plot(angles, pattern_db, label=f'Steer={steer_angle}°', linewidth=2)
        
    ax2.set_xlabel('Angle (degrees)')
    ax2.set_ylabel('Normalized Pattern (dB)')
    ax2.set_title('Beam Patterns (Rectangular)')
    ax2.set_xlim([-90, 90])
    ax2.set_ylim([-60, 0])
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('beam_patterns.png', dpi=300)
    print(f"Beam pattern plot saved to beam_patterns.png")


def generate_test_vectors(output_file='test_vectors.txt'):
    """Generate test vectors for testbench"""
    
    bf = BeamformerReference(num_channels=48, spacing=0.5, sample_rate=500e6)
    
    # Test case: signal from 0°, beam steered to 0°
    signals = bf.generate_signal(
        angle_deg=0.0,
        freq=10e6,
        amplitude=0.1,
        num_samples=1000
    )
    
    output = bf.beamform(signals, steering_angle_deg=0.0)
    
    # Save to file
    with open(output_file, 'w') as f:
        f.write("# Test vectors for beamformer verification\n")
        f.write("# Format: sample_idx, expected_real, expected_imag, magnitude\n")
        
        for i in range(len(output)):
            magnitude = np.abs(output[i])
            f.write(f"{i}, {output[i].real:.6e}, {output[i].imag:.6e}, {magnitude:.6e}\n")
            
    print(f"Test vectors saved to {output_file}")
    
    # Print summary
    print(f"\nExpected output statistics:")
    print(f"  Peak magnitude: {np.max(np.abs(output)):.3e}")
    print(f"  Mean magnitude: {np.mean(np.abs(output)):.3e}")
    print(f"  Expected gain (dB): {20*np.log10(48):.1f} dB (coherent sum of 48 elements)")


def main():
    """Main execution"""
    
    print("Beamformer Analysis Tool")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'analyze':
            analyze_results()
        elif sys.argv[1] == 'patterns':
            plot_beam_patterns()
        elif sys.argv[1] == 'vectors':
            generate_test_vectors()
        elif sys.argv[1] == 'all':
            generate_test_vectors()
            plot_beam_patterns()
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python beamformer_analysis.py [analyze|patterns|vectors|all]")
    else:
        # Default: generate patterns
        print("\nGenerating beam patterns...")
        plot_beam_patterns()
        print("\nFor full analysis, run after simulation:")
        print("  python beamformer_analysis.py analyze")


if __name__ == '__main__':
    main()