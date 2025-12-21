from app.engine.policy import CircuitBreakerPolicy


def test_policy_transitions_to_halt():
    p = CircuitBreakerPolicy()
    assert p.get_state()["state"] == "NORMAL"

    out = p.update(symbol="RELIANCE", score=95.0, reasons=["attack_scenario"])
    assert out["state"] == "HALT"
