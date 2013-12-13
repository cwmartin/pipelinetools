import unittest
import os
from pipelinetools.utils import environment


class TestEnvironment(unittest.TestCase):

    def setUp(self):
        """
        """
        self.environment = environment.Environment()

    def test_splitvals(self):
        """
        """
        expected = ["a", "b", "c", "d"]
        value = os.pathsep.join(expected)

        actual = self.environment.splitvals(value)

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()