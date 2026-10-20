import pytest


@pytest.mark.parametrize(
    ("path", "expected_status"),
    [
        ("/health/live", 200),
        ("/health/ready", 200),
        ("/api/products", 200),
        ("/missing-header-check", 404),
    ],
)
def test_content_type_options_header(client, path, expected_status):
    response = client.get(path)

    assert response.status_code == expected_status
    assert response.headers["X-Content-Type-Options"] == "nosniff"
