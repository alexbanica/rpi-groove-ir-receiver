import subprocess
import unittest
from unittest.mock import patch

from scripts.release_version import ReleaseVersionError, parse_release_tag


class ReleaseVersionTest(unittest.TestCase):
    def test_accepts_stable_tag_and_keeps_exact_distribution_version(self):
        parsed = parse_release_tag("1.2.3")

        self.assertEqual("1.2.3", parsed.tag)
        self.assertEqual("1.2.3", parsed.distribution_version)

    def test_accepts_beta_tag_and_maps_to_pep440(self):
        parsed = parse_release_tag("1.2.3-beta1")

        self.assertEqual("1.2.3-beta1", parsed.tag)
        self.assertEqual("1.2.3b1", parsed.distribution_version)

    def test_accepts_larger_numeric_components_without_normalizing_them(self):
        parsed = parse_release_tag("10.20.300-beta12")

        self.assertEqual("10.20.300b12", parsed.distribution_version)

    def test_missing_tag_has_a_deterministic_error(self):
        for tag in (None, ""):
            with self.subTest(tag=tag):
                with self.assertRaises(ReleaseVersionError) as context:
                    parse_release_tag(tag)

                self.assertEqual("release tag is required", str(context.exception))

    def test_rejected_tags_have_deterministic_errors(self):
        rejected_tags = (
            "v1.2.3",  # leading v
            " 1.2.3",  # leading whitespace
            "1.2.3 ",  # trailing whitespace
            "1. 2.3",  # embedded whitespace
            "1.2",  # missing version component
            "1.2.3.4",  # extra version component
            "01.2.3",  # leading zero in a version component
            "1.02.3",
            "1.2.03",
            "1.2.3-beta0",  # beta numbers start at one
            "1.2.3-beta01",  # beta number has a leading zero
            "1.2.3-beta.1",  # dotted prerelease
            "1.2.3-alpha1",  # arbitrary prerelease suffix
            "1.2.3-rc1",
            "1.2.3+build.1",  # build metadata
        )

        for tag in rejected_tags:
            with self.subTest(tag=tag):
                with self.assertRaises(ReleaseVersionError) as context:
                    parse_release_tag(tag)

                self.assertEqual(
                    f"unsupported release tag: {tag}", str(context.exception)
                )

    def test_parsing_does_not_execute_external_commands(self):
        with patch.object(subprocess, "run") as run, patch.object(
            subprocess, "Popen"
        ) as popen:
            parsed = parse_release_tag("2.0.0-beta1")
            self.assertEqual("2.0.0b1", parsed.distribution_version)

        run.assert_not_called()
        popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
