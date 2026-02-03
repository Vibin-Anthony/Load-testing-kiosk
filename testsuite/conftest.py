import time
import pytest
import os
import glob

def pytest_collection_modifyitems(items):
    for file in glob.glob("*.png"):
        os.remove(file)

    for file in glob.glob("/tmp/testsuite_screenshots/*.png"):
        os.remove(file)
    """Ensure tests run in a specific order"""
    test_order = [
        "test_startup.py",
        "test_loyalty.py",
        "test_collection.py",
        "test_checkout.py",
        "test_offline.py"
    ]

    # Sort items based on test_order list
    items.sort(key=lambda item: test_order.index(item.fspath.basename) if item.fspath.basename in test_order else len(test_order))

@pytest.fixture()
def fixture():
    for file in glob.glob("*.png"):
        os.remove(file)

    for file in glob.glob("/tmp/testsuite_screenshots/*.png"):
        os.remove(file)
    
    time.sleep(2)
    yield