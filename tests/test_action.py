from unittest.mock import MagicMock, patch

import pytest
from github_action_template.framework import GitHubEnvironment

from check_pr_comment.action import CheckPRCommentAction


@patch('builtins.print')
@patch("github_action_template.framework.GitHub")
def test_action_not_a_pr(mock_github, mock_print):
    github_env = MagicMock(spec=GitHubEnvironment)

    action = CheckPRCommentAction(github_env)
    action.run()

    mock_github.assert_not_called()
    assert mock_print.mock_calls and mock_print.mock_calls[0].args
    assert "::warning::" in mock_print.mock_calls[0].args[0]


@pytest.mark.parametrize("body, must, must_not, review_text", [
    ("", "REQUIRED", "FORBIDDEN", "Please add a descriptive text to this pull request.\n\n"
                                  "Pull request text should contain this snippet: `REQUIRED`."),
    ("TEXT", "REQUIRED", "FORBIDDEN", "Pull request text should contain this snippet: `REQUIRED`."),
    ("TEXT+REQUIRED+TEXT", "REQUIRED", "FORBIDDEN", ""),
    ("TEXT+FORBIDDEN+TEXT", "REQUIRED", "FORBIDDEN", "Pull request text should contain this snippet: `REQUIRED`.\n\n"
                                                     "Pull request text should not contain this snippet: `FORBIDDEN`."),
    ("TEXT+FORBIDDEN+REQUIRED+TEXT", "REQUIRED", "FORBIDDEN", "Pull request text should not "
                                                              "contain this snippet: `FORBIDDEN`."),
    ])
def test_action_pull_request(body, must, must_not, review_text):
    with patch("github_action_template.framework.GitHub") as mock_github:
        github_env = GitHubEnvironment(
            {"INPUT_COMMENTS-MUST-CONTAIN": must,
             "INPUT_COMMENTS-MUST-NOT-CONTAIN": must_not,
             "GITHUB_EVENT_NAME": "pull_request",
             "GITHUB_TOKEN": "TOKEN",
             })
        github_env._cached_json_payload = {
            "repository": {"owner": {"login": "alogin"},
                           "name": "repo_name"
                           },
            "pull_request": {"number": "1",
                             "body": body
                             }
            }

        action = CheckPRCommentAction(github_env)
        action.run()

        if review_text:
            mock_github.return_value.pull_request.assert_called_with("alogin", "repo_name", "1")
            mock_github.return_value.pull_request.return_value.create_review.assert_called_once_with(
                review_text, event='REQUEST_CHANGES')
        else:
            mock_github.assert_not_called()
