from local_test import BaseTestClass


class ThisTestClass(BaseTestClass):
    """
    This test exists to make test discovery succeed (until a real test is added).
    """

    def test_dummy(self):
        self.assertTrue(True)
