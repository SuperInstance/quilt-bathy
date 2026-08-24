"""Integration test: substrate-trainer on the bathy chart."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "quilt-substrate", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "substrate-trainer", "src"))
from bathy import BathyChart, Sailor, ConvoyBoat
from trainer import Trainer


def test_bathy_chart_provides_training_data():
    """The bathy chart produces a witness log the trainer can learn from."""
    chart = BathyChart()
    for i in range(5):
        boat = ConvoyBoat(name=f"boat-{i:02d}")
        for x, y, d in boat.survey(n=5):
            chart.add_convoy_sounding(x, y, d, agent=boat.name)
    reyes = Sailor(name="reyes")
    for x, y, d in reyes.survey(n=20):
        chart.add_sounding(x, y, d, agent=reyes.name)

    trainer = Trainer()
    model = trainer.fit(chart.substrate, n_epochs=5)

    # The model should have seen at least one agent
    assert len(model.agent_to_id) > 0
    # The model should have been trained
    assert model.n_train > 0


def test_model_predicts_mean_depth():
    """After training on the chart, the model predicts close to the mean depth."""
    chart = BathyChart()
    for i in range(10):
        boat = ConvoyBoat(name=f"boat-{i:02d}")
        for x, y, d in boat.survey(n=10):
            chart.add_convoy_sounding(x, y, d, agent=boat.name)
    reyes = Sailor(name="reyes")
    for x, y, d in reyes.survey(n=50):
        chart.add_sounding(x, y, d, agent=reyes.name)

    trainer = Trainer()
    model = trainer.fit(chart.substrate, n_epochs=20)

    pred, conf = model.predict(["reyes"])
    # The bathy values are between 5 and 30
    assert 5.0 < pred < 30.0


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
