"""
Tree Unwrap Visualization Tool

This script "unwraps" the 3D Christmas tree into a 2D cylindrical projection,
divides it into 16 angular sections, and visualizes spatial relationships
between LEDs to help verify face mapping for 3D grid-like light triggering.

Usage:
    python tree_unwrap_viz.py                    # Generate all visualizations
    python tree_unwrap_viz.py --no-neighbors     # Skip neighbor lines (faster)
    python tree_unwrap_viz.py --sections 8       # Use 8 sections instead of 16

Output:
    - tree_unwrap.png: 2D unwrapped view with section coloring
    - tree_sections_3d.png: 3D matplotlib view with same coloring
    - Console statistics about section distribution and spatial patterns
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import KDTree
import argparse
from utils.geometry import POINTS_3D


def cylindrical_coords(points):
    """
    Convert 3D Cartesian coordinates to cylindrical (r, theta, z).
    
    Args:
        points: numpy array of shape (N, 3) with [x, y, z] coordinates
        
    Returns:
        r: distance from center axis
        theta: angle in radians [0, 2*pi)
        z: height (unchanged)
    """
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)  # Returns [-pi, pi]
    theta = (theta + 2 * np.pi) % (2 * np.pi)  # Normalize to [0, 2*pi)
    return r, theta, z


def assign_sections(theta, num_sections=16):
    """
    Assign each LED to an angular section.
    
    Args:
        theta: array of angles in radians [0, 2*pi)
        num_sections: number of sections to divide the tree into
        
    Returns:
        section_ids: array of section indices (0 to num_sections-1)
    """
    section_width = 2 * np.pi / num_sections
    section_ids = (theta / section_width).astype(int) % num_sections
    return section_ids


def get_section_colors(num_sections):
    """
    Generate distinct colors for each section using a perceptually uniform colormap.
    
    Args:
        num_sections: number of sections
        
    Returns:
        colors: list of RGBA tuples
    """
    cmap = plt.cm.get_cmap('tab20' if num_sections <= 20 else 'hsv')
    colors = [cmap(i / num_sections) for i in range(num_sections)]
    return colors


def compute_nearest_neighbors(points, k=3):
    """
    Compute k nearest neighbors for each LED.
    
    Args:
        points: numpy array of shape (N, 3)
        k: number of nearest neighbors
        
    Returns:
        neighbor_pairs: list of (i, j) index pairs for neighbor connections
    """
    tree = KDTree(points)
    distances, indices = tree.query(points, k=k+1)  # +1 because point is its own neighbor
    
    neighbor_pairs = []
    for i in range(len(points)):
        for j in indices[i, 1:]:  # Skip first (self)
            if i < j:  # Avoid duplicates
                neighbor_pairs.append((i, j))
    
    return neighbor_pairs


def analyze_sequential_continuity(points, window=10):
    """
    Analyze if sequential LED indices are spatially close.
    
    This helps understand the physical stringing pattern.
    
    Args:
        points: numpy array of shape (N, 3)
        window: number of neighbors to check
        
    Returns:
        stats: dictionary with continuity statistics
    """
    n = len(points)
    avg_sequential_dist = []
    avg_random_dist = []
    
    for i in range(n - 1):
        # Distance to next sequential LED
        seq_dist = np.linalg.norm(points[i] - points[i + 1])
        avg_sequential_dist.append(seq_dist)
        
        # Distance to a random LED (for comparison)
        random_idx = np.random.randint(0, n)
        while random_idx == i:
            random_idx = np.random.randint(0, n)
        rand_dist = np.linalg.norm(points[i] - points[random_idx])
        avg_random_dist.append(rand_dist)
    
    return {
        'avg_sequential_distance': np.mean(avg_sequential_dist),
        'std_sequential_distance': np.std(avg_sequential_dist),
        'avg_random_distance': np.mean(avg_random_dist),
        'continuity_ratio': np.mean(avg_sequential_dist) / np.mean(avg_random_dist),
        'max_sequential_jump': np.max(avg_sequential_dist),
        'min_sequential_distance': np.min(avg_sequential_dist),
    }


def plot_2d_unwrap(theta, z, section_ids, num_sections, colors, 
                   neighbor_pairs=None, points_3d=None, show_neighbors=True,
                   save_path='tree_unwrap.png'):
    """
    Create 2D unwrapped visualization.
    
    Args:
        theta: angles in radians
        z: heights
        section_ids: section assignment for each LED
        num_sections: total number of sections
        colors: color for each section
        neighbor_pairs: optional list of (i, j) neighbor connections
        points_3d: original 3D points (for neighbor line calculations)
        show_neighbors: whether to draw neighbor connection lines
        save_path: output file path
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Convert theta to degrees for readability
    theta_deg = np.degrees(theta)
    
    # Draw neighbor connection lines first (so dots are on top)
    if show_neighbors and neighbor_pairs is not None:
        # Create line segments in 2D unwrapped space
        # Need to handle wraparound at 0/360 degrees
        lines = []
        line_colors = []
        
        for i, j in neighbor_pairs:
            t1, t2 = theta_deg[i], theta_deg[j]
            z1, z2 = z[i], z[j]
            
            # Check if line wraps around (crosses 0/360 boundary)
            if abs(t1 - t2) > 180:
                # Line wraps - skip for clarity (or could draw two segments)
                continue
            
            lines.append([(t1, z1), (t2, z2)])
            # Color based on average section
            avg_section = (section_ids[i] + section_ids[j]) // 2
            line_colors.append((*colors[avg_section][:3], 0.15))  # Transparent
        
        lc = LineCollection(lines, colors=line_colors, linewidths=0.5)
        ax.add_collection(lc)
    
    # Draw section boundary lines
    section_width_deg = 360 / num_sections
    for i in range(num_sections + 1):
        boundary = i * section_width_deg
        ax.axvline(x=boundary, color='gray', linestyle='--', alpha=0.5, linewidth=0.5)
    
    # Scatter plot of LEDs, colored by section
    for section in range(num_sections):
        mask = section_ids == section
        ax.scatter(theta_deg[mask], z[mask], c=[colors[section]], 
                   s=30, alpha=0.8, label=f'Section {section}')
    
    # Add section labels at top
    for i in range(num_sections):
        center = (i + 0.5) * section_width_deg
        count = np.sum(section_ids == i)
        ax.text(center, z.max() + 0.05, f'{i}\n({count})', 
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Add sparse index labels (every 50th LED)
    for idx in range(0, len(theta_deg), 50):
        ax.annotate(str(idx), (theta_deg[idx], z[idx]), 
                    fontsize=6, alpha=0.7, 
                    xytext=(3, 3), textcoords='offset points')
    
    # Formatting
    ax.set_xlabel('Angle (degrees)', fontsize=12)
    ax.set_ylabel('Height (Z)', fontsize=12)
    ax.set_title(f'Tree Unwrapped View - {num_sections} Sections\n'
                 f'(Numbers at top show section ID and LED count)', fontsize=14)
    ax.set_xlim(-5, 365)
    ax.set_ylim(z.min() - 0.1, z.max() + 0.15)
    ax.grid(True, alpha=0.3)
    
    # Add degree markers
    ax.set_xticks(np.arange(0, 361, 45))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved 2D unwrapped view to: {save_path}")
    plt.close()


def plot_3d_sections(points, section_ids, num_sections, colors, 
                     save_path='tree_sections_3d.png'):
    """
    Create 3D visualization with section coloring.
    
    Args:
        points: numpy array of shape (N, 3)
        section_ids: section assignment for each LED
        num_sections: total number of sections
        colors: color for each section
        save_path: output file path
    """
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot each section with its color
    for section in range(num_sections):
        mask = section_ids == section
        ax.scatter(points[mask, 0], points[mask, 1], points[mask, 2],
                   c=[colors[section]], s=20, alpha=0.8, label=f'Section {section}')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z (Height)')
    ax.set_title(f'3D Tree with {num_sections} Angular Sections')
    
    # Set equal aspect ratio
    max_range = np.array([
        points[:, 0].max() - points[:, 0].min(),
        points[:, 1].max() - points[:, 1].min(),
        points[:, 2].max() - points[:, 2].min()
    ]).max() / 2.0
    
    mid_x = (points[:, 0].max() + points[:, 0].min()) * 0.5
    mid_y = (points[:, 1].max() + points[:, 1].min()) * 0.5
    mid_z = (points[:, 2].max() + points[:, 2].min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Saved 3D section view to: {save_path}")
    plt.close()


def print_statistics(section_ids, num_sections, continuity_stats, r, theta, z):
    """Print analysis statistics to console."""
    print("\n" + "="*60)
    print("TREE FACE MAPPING ANALYSIS")
    print("="*60)
    
    print(f"\n📊 SECTION DISTRIBUTION ({num_sections} sections):")
    print("-" * 40)
    for section in range(num_sections):
        count = np.sum(section_ids == section)
        start_deg = section * (360 / num_sections)
        end_deg = (section + 1) * (360 / num_sections)
        bar = "█" * (count // 2)
        print(f"  Section {section:2d} ({start_deg:5.1f}°-{end_deg:5.1f}°): {count:3d} LEDs {bar}")
    
    print(f"\n📏 COORDINATE RANGES:")
    print("-" * 40)
    print(f"  Radius (r):  {r.min():.4f} to {r.max():.4f}")
    print(f"  Height (z):  {z.min():.4f} to {z.max():.4f}")
    print(f"  Angle range: 0° to 360°")
    
    print(f"\n🔗 SEQUENTIAL CONTINUITY ANALYSIS:")
    print("-" * 40)
    print(f"  Avg distance between sequential LEDs: {continuity_stats['avg_sequential_distance']:.4f}")
    print(f"  Std deviation: {continuity_stats['std_sequential_distance']:.4f}")
    print(f"  Avg distance between random LEDs: {continuity_stats['avg_random_distance']:.4f}")
    print(f"  Continuity ratio: {continuity_stats['continuity_ratio']:.4f}")
    print(f"    (< 1.0 means sequential LEDs are closer than random)")
    print(f"  Max jump between sequential LEDs: {continuity_stats['max_sequential_jump']:.4f}")
    print(f"  Min distance between sequential LEDs: {continuity_stats['min_sequential_distance']:.4f}")
    
    # Interpret the pattern
    ratio = continuity_stats['continuity_ratio']
    if ratio < 0.3:
        pattern = "Strong spatial continuity - LEDs likely strung in a continuous path"
    elif ratio < 0.6:
        pattern = "Moderate continuity - LEDs roughly follow a spatial pattern"
    else:
        pattern = "Weak continuity - LED indices may not follow physical stringing order"
    
    print(f"\n  🎯 Interpretation: {pattern}")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Unwrap and visualize tree LED mapping')
    parser.add_argument('--sections', type=int, default=16, 
                        help='Number of angular sections (default: 16)')
    parser.add_argument('--no-neighbors', action='store_true',
                        help='Skip neighbor line visualization')
    parser.add_argument('--k-neighbors', type=int, default=3,
                        help='Number of nearest neighbors to show (default: 3)')
    args = parser.parse_args()
    
    num_sections = args.sections
    show_neighbors = not args.no_neighbors
    k_neighbors = args.k_neighbors
    
    print(f"Loading {len(POINTS_3D)} LED coordinates...")
    
    # Convert to cylindrical coordinates
    r, theta, z = cylindrical_coords(POINTS_3D)
    
    # Assign sections
    section_ids = assign_sections(theta, num_sections)
    
    # Get colors
    colors = get_section_colors(num_sections)
    
    # Analyze sequential continuity
    continuity_stats = analyze_sequential_continuity(POINTS_3D)
    
    # Compute nearest neighbors if needed
    neighbor_pairs = None
    if show_neighbors:
        print(f"Computing {k_neighbors}-nearest neighbors...")
        neighbor_pairs = compute_nearest_neighbors(POINTS_3D, k=k_neighbors)
        print(f"  Found {len(neighbor_pairs)} unique neighbor pairs")
    
    # Print statistics
    print_statistics(section_ids, num_sections, continuity_stats, r, theta, z)
    
    # Generate visualizations
    print("Generating 2D unwrapped visualization...")
    plot_2d_unwrap(theta, z, section_ids, num_sections, colors,
                   neighbor_pairs=neighbor_pairs, points_3d=POINTS_3D,
                   show_neighbors=show_neighbors)
    
    print("Generating 3D section visualization...")
    plot_3d_sections(POINTS_3D, section_ids, num_sections, colors)
    
    print("\n✅ Done! Check tree_unwrap.png and tree_sections_3d.png")


if __name__ == '__main__':
    main()

