import pytest
from rangyuu.provider import HttpProvider
def test_provider_requires_https_and_blocks_private():
 for url in ("http://example.com","https://127.0.0.1","https://10.0.0.1"):
  with pytest.raises(ValueError): HttpProvider(url)
