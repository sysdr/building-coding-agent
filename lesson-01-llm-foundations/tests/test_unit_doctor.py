"""Unit tests for the environment doctor."""
import unittest

from apr import doctor


class TestDoctor(unittest.TestCase):
    def test_run_all_returns_three_checks(self):
        self.assertEqual(len(doctor.run_all()), 3)

    def test_python_check_passes_on_this_interpreter(self):
        self.assertTrue(doctor.check_python().ok)

    def test_docker_missing_is_not_critical(self):
        result = doctor.CheckResult("docker", False, "not found")
        self.assertFalse(result.critical)
        self.assertIn("WARN", result.render())

    def test_all_critical_pass_ignores_non_critical_failures(self):
        results = [
            doctor.CheckResult("python", True, ""),
            doctor.CheckResult("git", True, ""),
            doctor.CheckResult("docker", False, ""),
        ]
        self.assertTrue(doctor.all_critical_pass(results))

    def test_failing_critical_check_renders_fail(self):
        self.assertIn("FAIL", doctor.CheckResult("git", False, "").render())


if __name__ == "__main__":
    unittest.main()
