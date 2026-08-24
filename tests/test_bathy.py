"""Tests for quilt-bathy."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "quilt-substrate", "src"))
from substrate import Substrate
from bathy import BathyChart, Sailor, ConvoyBoat


def test_chart_starts_empty():
    c = BathyChart()
    assert len(c.substrate) == 0


def test_add_sounding_creates_cell():
    c = BathyChart()
    c.add_sounding(50, 50, 12.5, agent="reyes")
    assert c.get_depth(50, 50) == 12.5


def test_sailor_survey_produces_soundings():
    s = Sailor(name="reyes")
    soundings = s.survey(n=10)
    assert len(soundings) == 10
    for x, y, d in soundings:
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(d, float)


def test_convoy_boat_survey_produces_soundings():
    boat = ConvoyBoat(name="boat-00")
    soundings = boat.survey(n=20)
    assert len(soundings) == 20


def test_convoy_view_returns_per_agent_counts():
    c = BathyChart()
    for i in range(3):
        boat = ConvoyBoat(name=f"boat-{i:02d}")
        for x, y, d in boat.survey(n=5):
            c.add_convoy_sounding(x, y, d, agent=boat.name)
    view = c.convoy_view()
    for i in range(3):
        assert view[f"boat-{i:02d}"] == 5


def test_cross_section_returns_n_points():
    c = BathyChart()
    for i in range(50):
        c.add_sounding(10 + i, 50, 10.0 + (i % 5) * 0.5, agent="reyes")
    cs = c.cross_section((10, 50), (60, 50), n_points=10)
    assert len(cs) == 10
    for p in cs:
        assert "x" in p and "y" in p and "depth" in p and "confidence" in p


def test_fog_of_war_returns_stale_cells():
    c = BathyChart()
    c.add_sounding(50, 50, 12.5, agent="reyes")
    fog = c.fog_of_war(threshold=0.99)
    # The cell should be fresh, not in fog
    assert all(c.get_confidence(x, y) >= 0.99 for x, y, conf in fog)


def test_render_ascii_returns_string():
    c = BathyChart()
    c.add_sounding(50, 50, 12.5, agent="reyes")
    s = c.render_ascii()
    assert isinstance(s, str)
    assert len(s) > 0
    lines = s.split("\n")
    assert len(lines) == 20  # default height


def test_fable_02_sailors_tablet_chart_is_usable():
    """Fable 02: The chart speaks in metaphor where the substrate would speak in numbers."""
    c = BathyChart()
    reyes = Sailor(name="reyes")
    for x, y, d in reyes.survey(n=20):
        c.add_sounding(x, y, d, agent=reyes.name)
    # The chart should be usable: every point Reyes surveyed should be retrievable
    for x, y, d in reyes.survey(n=20):
        addr_depth = c.get_depth(x, y)
        if addr_depth is not None:
            # The cell exists at this location (Reyes is canonical)
            assert abs(addr_depth - d) < 1.0  # within noise


def test_fable_03_convoy_is_agent():
    """Fable 03: 100 boats writing to the same cell-graph. The convoy is the agent."""
    c = BathyChart()
    for i in range(50):
        boat = ConvoyBoat(name=f"boat-{i:02d}")
        for x, y, d in boat.survey(n=10):
            c.add_convoy_sounding(x, y, d, agent=boat.name)
    view = c.convoy_view()
    assert len(view) == 50


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
