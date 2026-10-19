import json
import tempfile
import unittest
from pathlib import Path

from agent_harness import Agent, WorkspaceTools


class FakeModel:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.seen = []

    def complete(self, messages, tools):
        self.seen.append((list(messages), list(tools)))
        return next(self.replies)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "note.txt").write_text("hello", encoding="utf-8")

    def test_agent_feeds_tool_result_back_to_model(self):
        model = FakeModel(
            [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "read_file",
                                "arguments": {"path": "note.txt"},
                            }
                        }
                    ],
                },
                {"role": "assistant", "content": "The file says hello."},
            ]
        )
        agent = Agent(model, WorkspaceTools(self.root))
        result = agent.run("Read the note", trace=True)
        self.assertEqual(result.answer, "The file says hello.")
        self.assertEqual(result.steps, 2)
        self.assertEqual(result.trace[0]["result"]["result"]["content"], "hello")
        self.assertEqual(model.seen[1][0][-1]["role"], "tool")
        available_names = [tool["function"]["name"] for tool in model.seen[0][1]]
        self.assertNotIn("write_file", available_names)

    def test_path_cannot_escape_workspace(self):
        tools = WorkspaceTools(self.root)
        result = json.loads(tools.execute("read_file", {"path": "../outside.txt"}))
        self.assertFalse(result["ok"])
        self.assertIn("escapes", result["error"])

    def test_git_metadata_is_not_accessible(self):
        tools = WorkspaceTools(self.root, allow_write=True)
        response = tools.execute(
            "write_file", {"path": ".git/config", "content": "x"}
        )
        result = json.loads(response)
        self.assertFalse(result["ok"])
        self.assertIn("Git metadata", result["error"])

    def test_write_requires_flag_and_explicit_overwrite(self):
        readonly = WorkspaceTools(self.root)
        denied = readonly.execute("write_file", {"path": "new.txt", "content": "a"})
        self.assertFalse(json.loads(denied)["ok"])
        writable = WorkspaceTools(self.root, allow_write=True)
        first = json.loads(
            writable.execute("write_file", {"path": "new.txt", "content": "a"})
        )
        second = json.loads(
            writable.execute("write_file", {"path": "new.txt", "content": "b"})
        )
        third = json.loads(
            writable.execute(
                "write_file",
                {"path": "new.txt", "content": "b", "overwrite": True},
            )
        )
        self.assertTrue(first["ok"])
        self.assertFalse(second["ok"])
        self.assertTrue(third["ok"])
        self.assertEqual((self.root / "new.txt").read_text(encoding="utf-8"), "b")

    def test_step_limit_stops_repeated_tool_calls(self):
        call = {
            "role": "assistant",
            "tool_calls": [{"function": {"name": "list_files", "arguments": {}}}],
        }
        agent = Agent(FakeModel([call, call]), WorkspaceTools(self.root), max_steps=2)
        result = agent.run("List files")
        self.assertTrue(result.stopped_by_limit)
        self.assertEqual(result.steps, 2)


if __name__ == "__main__":
    unittest.main()
