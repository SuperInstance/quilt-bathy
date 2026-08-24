"""
quilt-bathy — The bathy cross-section as a working tool.

A thin wrapper around quilt-substrate, applied to the sailor's actual use case.
The Inner Sound. The convoy. The cross-section. The fog of war.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
import os
import sys
import math
import random

# We depend on quilt-substrate
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "quilt-substrate", "src"))
    from substrate import Substrate, Cell
    HAS_SUBSTRATE = True
except ImportError:
    HAS_SUBSTRATE = False
    Substrate = None
    Cell = None


# -- BathyChart ------------------------------------------------------------

class BathyChart:
    """The bathy chart. A substrate of depth cells, indexed by (x, y)."""

    def __init__(self, bounds: Optional[Dict[str, Tuple[float, float]]] = None, resolution: float = 5.0):
        """Create a chart. Bounds is a dict like {axis: (min, max)}.
        Resolution is the cell size (in coordinate units)."""
        if not HAS_SUBSTRATE:
            raise ImportError("quilt-substrate required: pip install quilt-substrate")
        self.bounds = bounds or {"x": (0, 100), "y": (0, 100), "depth": (0, 30)}
        self.resolution = resolution
        self.substrate = Substrate()

    def _address(self, x: float, y: float) -> str:
        """Address for a (x, y) cell. Rounded to the resolution grid."""
        gx = round(x / self.resolution)
        gy = round(y / self.resolution)
        return f"bay/{gx:04d}x{gy:04d}"

    def add_sounding(self, x: float, y: float, depth: float, agent: str = "default") -> None:
        """Add a single sounding. Creates the cell if it doesn't exist; refreshes it if it does."""
        addr = self._address(x, y)
        cell = self.substrate.get(addr)
        if cell is None:
            cell = Cell(
                address=addr,
                value=depth,
                tensor=[depth],
                axes=("depth",),
            )
            self.substrate.add(cell)
        else:
            # Update value and refresh
            cell.value = depth
            cell.refresh()
        # Witness
        self.substrate.witness(cell, agent, "write", depth)
        self.substrate.witness(cell, agent, "read", depth)

    def add_convoy_sounding(self, x: float, y: float, depth: float, agent: str) -> None:
        """Add a convoy sounding. Inferred (not canonical)."""
        self.add_sounding(x, y, depth, agent=agent)
        # Inferences are not canonical
        self.substrate.infer(self._address(x, y), depth, agent_id=agent)

    def refresh(self, x: float, y: float) -> None:
        """Refresh the cell at (x, y). Resets the decay clock."""
        addr = self._address(x, y)
        self.substrate.refresh(addr)

    def get_depth(self, x: float, y: float) -> Optional[float]:
        """Get the current depth at (x, y)."""
        cell = self.substrate.get(self._address(x, y))
        return cell.value if cell else None

    def get_confidence(self, x: float, y: float) -> float:
        """Get the current confidence at (x, y)."""
        cell = self.substrate.get(self._address(x, y))
        return cell.confidence if cell else 0.0

    # -- Cross-section ------------------------------------------------------

    def cross_section(self, start: Tuple[float, float], end: Tuple[float, float], n_points: int = 20) -> List[Dict[str, Any]]:
        """Render a cross-section along a line from start to end.

        Returns a list of dicts with x, y, depth, confidence.
        For points where no data exists, depth is inferred (from neighboring cells).
        """
        x0, y0 = start
        x1, y1 = end
        result = []
        for i in range(n_points):
            t = i / max(1, n_points - 1)
            x = x0 + t * (x1 - x0)
            y = y0 + t * (y1 - y0)
            depth, conf = self._interpolate(x, y)
            result.append({"x": x, "y": y, "depth": depth, "confidence": conf})
        return result

    def _interpolate(self, x: float, y: float) -> Tuple[float, float]:
        """Get depth at (x, y). If no exact cell, infer from neighbors."""
        cell = self.substrate.get(self._address(x, y))
        if cell is not None:
            return cell.value, cell.confidence
        # Infer from neighbors
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx * self.resolution, y + dy * self.resolution
                ncell = self.substrate.get(self._address(nx, ny))
                if ncell is not None:
                    neighbors.append((ncell.value, ncell.confidence))
        if not neighbors:
            return 0.0, 0.0
        # Weighted average by confidence
        total_w = sum(c for _, c in neighbors)
        if total_w == 0:
            return sum(d for d, _ in neighbors) / len(neighbors), 0.0
        return sum(d * c for d, c in neighbors) / total_w, total_w / len(neighbors)

    # -- Fog of war --------------------------------------------------------

    def fog_of_war(self, threshold: float = 0.3) -> List[Tuple[float, float, float]]:
        """Return cells whose confidence is below threshold.

        Returns a list of (x, y, confidence) tuples.
        """
        stale = []
        for cell in self.substrate.all_cells():
            if cell.confidence < threshold:
                # Parse the address back to (x, y)
                # Address format: "bay/{gx:04d}x{gy:04d}"
                parts = cell.address.split("/")[1]
                gx, gy = parts.split("x")
                x = int(gx) * self.resolution
                y = int(gy) * self.resolution
                stale.append((x, y, cell.confidence))
        return stale

    # -- Convoy view -------------------------------------------------------

    def convoy_view(self) -> Dict[str, int]:
        """Return the number of cells written by each agent."""
        agents: Dict[str, int] = {}
        for cell in self.substrate.all_cells():
            for entry in cell.witness_log:
                if entry.action == "write":
                    agents[entry.agent_id] = agents.get(entry.agent_id, 0) + 1
        return agents

    # -- ASCII render ------------------------------------------------------

    def render_ascii(self, width: int = 60, height: int = 20) -> str:
        """Render the chart as ASCII art. For the terminal, for the satellite link."""
        xmin, xmax = self.bounds["x"]
        ymin, ymax = self.bounds["y"]
        dmin, dmax = self.bounds["depth"]
        # Sample on a grid
        lines = []
        for row in range(height):
            y = ymax - (ymax - ymin) * row / (height - 1)
            line = ""
            for col in range(width):
                x = xmin + (xmax - xmin) * col / (width - 1)
                depth, conf = self._interpolate(x, y)
                # Map depth/confidence to a character
                if conf < 0.2:
                    ch = " "  # fog
                else:
                    # Depth: shallow = ".", medium = ":", deep = "#"
                    norm = (depth - dmin) / max(0.01, dmax - dmin)
                    if norm < 0.3:
                        ch = "."
                    elif norm < 0.6:
                        ch = ":"
                    else:
                        ch = "#"
                line += ch
            lines.append(line)
        return "\n".join(lines)


# -- The Sailor ------------------------------------------------------------

@dataclass
class Sailor:
    """The user. Has her own high-resolution data."""
    name: str

    def survey(self, n: int = 50) -> List[Tuple[float, float, float]]:
        """Generate soundings along a serpentine path through the bay."""
        soundings = []
        for i in range(n):
            t = i / n
            x = 10 + 80 * t
            y = 50 + 30 * math.sin(t * math.pi * 3)
            d = 10 + 5 * math.sin(t * math.pi * 2) + random.uniform(-0.5, 0.5)
            soundings.append((x, y, d))
        return soundings


# -- The Convoy Boat --------------------------------------------------------

@dataclass
class ConvoyBoat:
    """One boat in the convoy. Writes to the substrate at lower density."""
    name: str

    def survey(self, n: int = 20) -> List[Tuple[float, float, float]]:
        """Generate sparse soundings across the whole bay."""
        soundings = []
        for _ in range(n):
            x = random.uniform(0, 100)
            y = random.uniform(20, 80)
            d = 5 + random.uniform(0, 20)
            soundings.append((x, y, d))
        return soundings


# -- CLI -------------------------------------------------------------------

def _cli():
    import argparse
    p = argparse.ArgumentParser(prog="quilt-bathy", description="The bathy cross-section as a working tool.")
    sub = p.add_subparsers(dest="cmd")
    demo = sub.add_parser("demo", help="Run a small demo: build a chart, render a cross-section.")
    args = p.parse_args()
    if args.cmd == "demo":
        chart = BathyChart()
        for i in range(10):
            boat = ConvoyBoat(name=f"boat-{i:02d}")
            for x, y, d in boat.survey(n=15):
                chart.add_convoy_sounding(x, y, d, agent=boat.name)
        reyes = Sailor(name="reyes")
        for x, y, d in reyes.survey(n=50):
            chart.add_sounding(x, y, d, agent=reyes.name)
        print(f"Chart: {len(chart.substrate)} cells")
        print("Convoy view:", chart.convoy_view())
        print()
        print("Cross-section (Reyes's planned tack):")
        cs = chart.cross_section((10, 50), (90, 50), n_points=15)
        for p in cs:
            print(f"  x={p['x']:.1f}, y={p['y']:.1f}, depth={p['depth']:.2f}, conf={p['confidence']:.3f}")
        print()
        print("ASCII render:")
        print(chart.render_ascii())
    else:
        p.print_help()


if __name__ == "__main__":
    _cli()
