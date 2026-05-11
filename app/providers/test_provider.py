from app.providers.mock_provider import MockProvider


def test_mock_provider_generates_response() -> None:
    provider = MockProvider()

    response = provider.generate(
        prompt="Question: What is DAGGER?",
        system_prompt="Answer from context.",
        temperature=0.0,
    )

    assert "MockProvider response" in response
    assert "DAGGER" in response