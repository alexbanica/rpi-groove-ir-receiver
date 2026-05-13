import unittest

from ir_receiver.applications.services.BurstSelectionService import BurstSelectionService


class BurstSelectionServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = BurstSelectionService()

    def test_returns_empty_when_no_capture_exists(self):
        self.assertEqual([], self.service.select([], 0))

    def test_returns_selected_index_when_valid(self):
        captures = [[1, 2], [3, 4], [5, 6]]
        self.assertEqual([3, 4], self.service.select(captures, 1))

    def test_defaults_to_first_capture_for_invalid_index(self):
        captures = [[1, 2], [3, 4], [5, 6]]
        self.assertEqual([1, 2], self.service.select(captures, 99))


if __name__ == "__main__":
    unittest.main()
