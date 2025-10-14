from unittest.mock import patch

from app.config.database import check_db_connection

print("Testing mock functionality...")

# Test the mock
with patch("app.config.database.create_engine") as mock_engine:
    print("Mock created successfully")
    mock_engine.side_effect = Exception("Test mock error")

    try:
        result = check_db_connection("test://")
        print("Result:", result)
    except Exception as e:
        print("Exception caught:", e)

print("Test completed")
