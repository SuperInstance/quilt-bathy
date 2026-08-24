"""
01-the-inner-sound.py — The Inner Sound, as a working tool.

The scenario: Reyes is sailing a small fishing boat across the Inner Sound
(at 57.2°N, 6.4°W — a real place, between Skye and the mainland). She has
a 12-inch tablet. The tablet shows the bathy chart of the bay. The chart
is backed by the substrate: every depth is a cell, every cell has a
confidence, every cell has a witness log.

The convoy is the other 10 boats in her fishing club. They have surveyed
the bay sparsely. The convoy's data is the substrate's witness log.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "quilt-substrate", "src"))
from bathy import BathyChart, Sailor, ConvoyBoat


def main():
    # Create the chart
    chart = BathyChart(bounds={"x": (0, 100), "y": (0, 100), "depth": (0, 30)})

    # Add the convoy: 10 boats, each writing sparse soundings
    for i in range(10):
        boat = ConvoyBoat(name=f"boat-{i:02d}")
        for x, y, d in boat.survey(n=15):
            chart.add_convoy_sounding(x, y, d, agent=boat.name)
    print(f"Convoy surveyed: {chart.convoy_view()}")

    # Add Reyes: her own high-resolution data
    reyes = Sailor(name="reyes")
    for x, y, d in reyes.survey(n=60):
        chart.add_sounding(x, y, d, agent=reyes.name)
    print(f"Total cells in chart: {len(chart.substrate)}")

    # Plan a tack
    print()
    print("Reyes's planned tack (a cross-section):")
    cs = chart.cross_section((10, 50), (90, 50), n_points=12)
    for p in cs:
        bar = "█" * int(p["depth"])
        marker = "👁" if p["confidence"] > 0.7 else "?"
        print(f"  x={p['x']:5.1f} | depth={p['depth']:5.2f}m | conf={p['confidence']:.2f} {marker} {bar}")

    # The fog of war
    print()
    print("Fog of war (cells with confidence < 0.7):")
    fog = chart.fog_of_war(threshold=0.7)
    print(f"  {len(fog)} cells are in the fog")

    # Render the chart
    print()
    print("The chart:")
    print(chart.render_ascii(width=70, height=18))


if __name__ == "__main__":
    main()
