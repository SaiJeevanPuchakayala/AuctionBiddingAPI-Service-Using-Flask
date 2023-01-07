from app import *


def test_get_all_CompletedAuctions():

    resp = get_all_CompletedAuctions()

    assert resp["result"] == "success"


if __name__ == "__main__":
    test_get_all_CompletedAuctions()
