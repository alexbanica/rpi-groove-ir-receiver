import unittest
from pathlib import Path

import yaml


WORKFLOW_DIR = Path(__file__).parents[1] / ".github" / "workflows"
CI_WORKFLOW = WORKFLOW_DIR / "ci.yml"
PUBLISH_WORKFLOW = WORKFLOW_DIR / "publish-forgejo.yml"

ALLOWED_STEP_KEYS = {
    "name",
    "uses",
    "run",
    "with",
    "env",
    "if",
    "shell",
    "working-directory",
    "timeout-minutes",
    "continue-on-error",
    "id",
}


def _workflow_text(path):
    """Read workflow content for narrow raw-text assertions."""
    if not path.is_file():
        raise AssertionError(f"workflow does not exist: {path}")
    return path.read_text(encoding="utf-8")


def _workflow(path):
    """Parse workflow as YAML with `on` preserved as a string key."""
    text = _workflow_text(path)
    parsed = yaml.load(text, Loader=yaml.BaseLoader)

    if not isinstance(parsed, dict):
        raise AssertionError(f"invalid workflow structure: {path}")

    return text, parsed


def _assert_mapping(value, location):
    if not isinstance(value, dict):
        raise AssertionError(f"{location} is not a mapping")


def _assert_list(value, location):
    if not isinstance(value, list):
        raise AssertionError(f"{location} is not a list")


def _step_by_name(steps, name):
    for step in steps:
        if step.get("name") == name:
            return step
    raise AssertionError(f"missing workflow step: {name}")


def _assert_step_blocks(steps):
    _assert_list(steps, "jobs.*.steps")
    for step in steps:
        if not isinstance(step, dict):
            raise AssertionError("workflow step is not a mapping")

        unknown_keys = set(step.keys()) - ALLOWED_STEP_KEYS
        if unknown_keys:
            raise AssertionError(f"workflow step has unsupported keys: {', '.join(sorted(unknown_keys))}")

        if "name" not in step:
            raise AssertionError("workflow step missing name")
        if not isinstance(step["name"], str):
            raise AssertionError("workflow step name is not a string")
        if "ref" in step:
            raise AssertionError("workflow step has unsupported top-level ref")
        if "run" not in step and "uses" not in step:
            raise AssertionError(f"workflow step {step['name']} missing action or shell command")

        if step["name"] == "Ruff lint":
            if "ruff check" not in step.get("run", ""):
                raise AssertionError("Ruff lint step is missing ruff check command")

        if step["name"] == "Unit tests":
            if "python -m unittest discover -s tests -p 'test_*.py'" not in step.get("run", ""):
                raise AssertionError("Unit tests step is missing test command")

    return steps


class GitHubWorkflowsTest(unittest.TestCase):
    def test_ci_runs_for_pull_requests_to_main_and_pushes_to_main(self):
        _, workflow = _workflow(CI_WORKFLOW)

        _assert_mapping(workflow, "workflow root")
        _assert_mapping(workflow.get("on"), "workflow.on")
        self.assertEqual(set(workflow["on"].keys()), {"pull_request", "push"})

        pr_trigger = workflow["on"]["pull_request"]
        push_trigger = workflow["on"]["push"]
        _assert_mapping(pr_trigger, "workflow.on.pull_request")
        _assert_mapping(push_trigger, "workflow.on.push")
        self.assertEqual(pr_trigger["branches"], ["main"])
        self.assertEqual(push_trigger["branches"], ["main"])

    def test_ci_has_expected_permissions(self):
        workflow_text = _workflow_text(CI_WORKFLOW)
        _, workflow = _workflow(CI_WORKFLOW)

        self.assertNotIn("FORGEJO_PACKAGE_TOKEN", workflow_text)
        _assert_mapping(workflow.get("permissions"), "workflow.permissions")
        self.assertEqual(workflow["permissions"], {"contents": "read"})

    def test_ci_uses_python_3_10_and_3_11_without_a_3_9_job(self):
        _, workflow = _workflow(CI_WORKFLOW)

        matrix = workflow["jobs"]["test"]["strategy"]["matrix"]
        self.assertEqual(matrix["python-version"], ["3.10", "3.11"])
        self.assertNotIn("3.9", matrix["python-version"])

    def test_ci_job_and_step_structure(self):
        _, workflow = _workflow(CI_WORKFLOW)

        _assert_mapping(workflow.get("jobs"), "workflow.jobs")
        self.assertEqual(set(workflow["jobs"].keys()), {"test"})
        _assert_mapping(workflow["jobs"].get("test"), "workflow.jobs.test")
        _assert_list(workflow["jobs"]["test"].get("steps"), "workflow.jobs.test.steps")
        steps = _assert_step_blocks(workflow["jobs"]["test"]["steps"])
        self.assertEqual(
            [step["name"] for step in steps],
            [
                "Checkout repository",
                "Set up Python",
                "Install release tooling",
                "Ruff lint",
                "Unit tests",
            ],
        )

    def test_ci_step_names_are_literal_strings(self):
        workflow_text = _workflow_text(CI_WORKFLOW)

        self.assertNotRegex(workflow_text, r"(?m)^      - name: \|\s*$")
        _, workflow = _workflow(CI_WORKFLOW)
        steps = _assert_step_blocks(workflow["jobs"]["test"]["steps"])
        self.assertEqual(
            [step["name"] for step in steps],
            [
                "Checkout repository",
                "Set up Python",
                "Install release tooling",
                "Ruff lint",
                "Unit tests",
            ],
        )

    def test_publish_is_tag_only_and_has_no_pr_or_branch_trigger(self):
        workflow_text = _workflow_text(PUBLISH_WORKFLOW)
        _, workflow = _workflow(PUBLISH_WORKFLOW)

        _assert_mapping(workflow.get("on"), "workflow.on")
        self.assertEqual(list(workflow["on"].keys()), ["push"])
        _assert_mapping(workflow["on"].get("push"), "workflow.on.push")
        self.assertIn("tags", workflow["on"]["push"])
        self.assertNotIn("branches", workflow["on"]["push"])

        self.assertIn("- '[0-9]*.[0-9]*.[0-9]*'", workflow_text)
        self.assertIn("- '[0-9]*.[0-9]*.[0-9]*-beta[1-9][0-9]*'", workflow_text)
        self.assertNotIn("pull_request", workflow_text)
        self.assertEqual(
            workflow["on"]["push"]["tags"],
            ["[0-9]*.[0-9]*.[0-9]*", "[0-9]*.[0-9]*.[0-9]*-beta[1-9][0-9]*"],
        )
        self.assertNotIn("+", workflow_text)
        self.assertNotIn(r"\+", workflow_text)
        self.assertNotRegex(workflow_text, r"\[0-9\]\+")

    def test_publish_checks_out_the_tagged_ref_only_with_with_ref(self):
        _, workflow = _workflow(PUBLISH_WORKFLOW)

        _assert_mapping(workflow.get("jobs"), "workflow.jobs")
        _assert_mapping(workflow["jobs"].get("publish"), "workflow.jobs.publish")
        _assert_list(workflow["jobs"]["publish"].get("steps"), "workflow.jobs.publish.steps")
        steps = _assert_step_blocks(workflow["jobs"]["publish"]["steps"])

        checkout_step = _step_by_name(steps, "Checkout tagged ref")
        self.assertEqual(checkout_step.get("uses"), "actions/checkout@v7")
        self.assertEqual(checkout_step.get("with", {}).get("ref"), "${{ github.ref }}")

    def test_publish_has_read_only_permissions_job_scope(self):
        _, workflow = _workflow(PUBLISH_WORKFLOW)

        _assert_mapping(workflow.get("permissions"), "workflow.permissions")
        self.assertEqual(workflow["permissions"], {"contents": "read"})

    def test_publish_has_per_ref_non_canceling_concurrency(self):
        _, workflow = _workflow(PUBLISH_WORKFLOW)

        _assert_mapping(workflow.get("concurrency"), "workflow.concurrency")
        self.assertEqual(workflow["concurrency"]["group"], "forgejo-publish-${{ github.ref }}")
        self.assertEqual(workflow["concurrency"]["cancel-in-progress"], "false")

    def test_publish_scopes_credentials_and_release_tag_to_publish_step_only(self):
        workflow_text = _workflow_text(PUBLISH_WORKFLOW)
        _, workflow = _workflow(PUBLISH_WORKFLOW)

        self.assertEqual(workflow_text.count("secrets.FORGEJO_PACKAGE_TOKEN"), 1)
        self.assertEqual(workflow_text.count("secrets.FORGEJO_PACKAGE_USERNAME"), 1)
        steps = _assert_step_blocks(workflow["jobs"]["publish"]["steps"])
        publish_step = _step_by_name(steps, "Publish to Forgejo")

        self.assertEqual(
            publish_step.get("env"),
            {
                "RELEASE_TAG": "${{ github.ref_name }}",
                "FORGEJO_PACKAGE_USERNAME": "${{ secrets.FORGEJO_PACKAGE_USERNAME }}",
                "FORGEJO_PACKAGE_TOKEN": "${{ secrets.FORGEJO_PACKAGE_TOKEN }}",
            },
        )

    def test_publish_run_has_no_token_or_secret_args(self):
        _, workflow = _workflow(PUBLISH_WORKFLOW)
        steps = _assert_step_blocks(workflow["jobs"]["publish"]["steps"])
        publish_step = _step_by_name(steps, "Publish to Forgejo")

        run_command = publish_step.get("run", "")
        self.assertIn("python -m scripts.publish_forgejo", run_command)
        self.assertNotIn("--token", run_command)
        self.assertNotIn("TWINE_PASSWORD", run_command)

    def test_publish_workflow_does_not_publish_from_branch_or_pull_request_context(self):
        workflow_text = _workflow_text(PUBLISH_WORKFLOW)

        self.assertNotIn("pull_request", workflow_text)
        self.assertNotIn("refs/heads/", workflow_text)


if __name__ == "__main__":
    unittest.main()
