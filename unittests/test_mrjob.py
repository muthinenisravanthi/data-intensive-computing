import unittest

class TestChiSquaredCalculation(unittest.TestCase):
    """
    Unit tests for the Chi-Squared calculation logic within the reducer.
    """

    def setUp(self):
        # Initialize the mock object for testing
        self.mjob = MockMRJob(data=None)

    def test_perfect_match_zero_chi_squared(self):
        """Test case where Observed == Expected for all categories, resulting in Chi-Squared = 0."""
        # Input format: [O1, E1, O2, E2]
        # O1=10, E1=10 => (10-10)^2 / 10 = 0
        # O2=5, E2=5  => (5-5)^2 / 5 = 0
        test_values = [10, 10, 5, 5]
        result = self.mjob.reducer("TestKey", test_values)
        self.assertAlmostEqual(result["chi_squared"], 0.0, places=5)

    def test_significant_deviation_high_chi_squared(self):
        """Test case with a large deviation, resulting in a high Chi-Squared value."""
        # Scenario: We observed much more of Category 1 than expected.
        # O1=20, E1=10 => (20-10)^2 / 10 = 100 / 10 = 10.0
        # O2=5, E2=5  => 0
        # O3=0, E3=10 => (0-10)^2 / 10 = 100 / 10 = 10.0
        test_values = [20, 10, 5, 5, 0, 10]
        result = self.mjob.reducer("TestKey", test_values)
        # Expected: 10.0 + 0.0 + 10.0 = 20.0
        self.assertAlmostEqual(result["chi_squared"], 20.0, places=5)

    def test_moderate_deviation_mixed_result(self):
        """Test case with mixed deviations."""
        # O1=12, E1=10 => (12-10)^2 / 10 = 4 / 10 = 0.4
        # O2=8, E2=10 => (8-10)^2 / 10 = 4 / 10 = 0.4
        # O3=10, E3=10 => 0
        test_values = [12, 10, 8, 10, 10, 10]
        result = self.mjob.reducer("TestKey", test_values)
        # Expected: 0.4 + 0.4 + 0.0 = 0.8
        self.assertAlmostEqual(result["chi_squared"], 0.8, places=5)

    def test_empty_input(self):
        """Test case with no values provided."""
        result = self.mjob.reducer("TestKey", [])
        self.assertEqual(result["chi_squared"], 0.0)

    def test_division_by_zero_handling(self):
        """Test case where an Expected count (E) is zero."""
        # O1=10, E1=10 => 0
        # O2=5, E2=0  => Should result in 0 term due to handling
        # O3=0, E3=10 => 1.0
        test_values = [10, 10, 5, 0, 0, 10]
        result = self.mjob.reducer("TestKey", test_values)
        # Expected: 0.0 + 0.0 + 1.0 = 1.0
        self.assertAlmostEqual(result["chi_squared"], 1.0, places=5)

    def test_invalid_input_length(self):
        """Test case where the input list length is odd (violates O/E pairing)."""
        test_values = [10, 10, 5]
        with self.assertRaises(ValueError) as cm:
            self.mjob.reducer("TestKey", test_values)
        self.assertIn("must be pairs of (Observed, Expected)", str(cm.exception))

