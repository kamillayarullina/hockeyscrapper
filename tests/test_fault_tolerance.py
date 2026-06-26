import pytest
from unittest.mock import AsyncMock, patch
from parsers.base_parser import BaseParser, NetworkError

class MockScraper(BaseParser):
    """Minimal implementation of BaseParser to test its retry logic and fault tolerance."""
    async def parse(self, html: str) -> list[dict]:
        return [{"event": "Test KHL Game", "tickets": True}]

@pytest.mark.asyncio
async def test_qrt_01_parser_retry_isolation_on_network_failure():
    """
    QRT-01 (Reliability - Fault Tolerance):
    Verifies that the parser successfully handles temporary 5xx errors, attempts retries, 
    and recovers gracefully when a subsequent request succeeds.
    """
    config = {
        "name": "mock_khl_parser",
        "url": "https://ticket-hockey.ru",
        "_retry_attempts": 3,
        "_retry_backoff_base": 1,
        "_min_delay": 0.0,
        "_max_delay": 0.0,
        "proxy_disabled": True
    }
    
    parser = MockScraper(config=config)
    
    # Intercept _fetch_with_playwright to simulate failures followed by a success
    with patch.object(parser, "_fetch_with_playwright", new_callable=AsyncMock) as mock_fetch:
        # 1st attempt: TimeoutError/NetworkError, 2nd attempt: Success HTML
        mock_fetch.side_effect = [
            NetworkError("HTTP 502 Bad Gateway"),
            "<html><div class='game'>KHL Match</div></html>"
        ]
        
        events = await parser.run()
        
        # Verify parser isolated the error, retried, and processed the successful second response
        assert len(events) == 1
        assert events[0]["event"] == "Test KHL Game"
        assert mock_fetch.call_count == 2