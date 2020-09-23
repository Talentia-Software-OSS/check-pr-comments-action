"""CheckPRCommentAction class"""
from typing import List, Optional

from github_action_template.framework import EVENT_PULL_REQUEST, GitHubAction


class CheckPRCommentAction(GitHubAction):
    """
    A concrete action to check that a PR uses template (by searching for a given text) and that this template has been
    properly changed (by searching placeholder text that should have been replaced by real text).
    """

    def run(self, args: Optional[List[str]] = None) -> None:
        """
        Perform the check_pr_comment.
        Run all checks in sequence and create a review on PR if any problem is detected.
        :param args: action parameters passed using `with:` in workflow, in same order. Not used at this time.
        """
        if self.github_env.event_name != EVENT_PULL_REQUEST:
            self.warning(f"This is not a Pull Request. This action should only be run 'on: [ {EVENT_PULL_REQUEST} ]'")
            return

        problems = [problem
                    for check in (self.check_has_body, self.check_must_contain, self.check_must_not_contain)
                    if (problem := check())]
        if problems:
            print(f"Creating a change request on PR for {len(problems)} problems: {problems}.")
            pull_request = self.get_pull_request_api_from_event()
            pull_request.create_review("\n\n".join(problems), event="REQUEST_CHANGES")
        else:
            print("No problem found.")

    def check_has_body(self) -> Optional[str]:
        """
        Check that there is at least some text in PR.
        :return: issue description if any, or None
        """
        pr_body_text = self.github_env.event_payload_find("pull_request/body")
        if not pr_body_text:
            return "Please add a descriptive text to this pull request."

    def check_must_contain(self) -> Optional[str]:
        """
        Check that required text, if any, can be found.
        :return: issue description if any, or None
        """
        must_contain = self.get_input("comments-must-contain", "")
        if must_contain:
            pr_body_text = self.github_env.event_payload_find("pull_request/body")
            if pr_body_text and must_contain in pr_body_text:
                print(f"OK, found `{must_contain}`.")
                return
            return f"Pull request text should contain this snippet: `{must_contain}`."

    def check_must_not_contain(self) -> Optional[str]:
        """
        Check that forbidden text, if any, cannot be found.
        :return: issue description if any, or None
        """
        must_not_contain = self.get_input("comments-must-not-contain", "")
        if must_not_contain:
            pr_body_text = self.github_env.event_payload_find("pull_request/body")
            if pr_body_text and must_not_contain in pr_body_text:
                return f"Pull request text should not contain this snippet: `{must_not_contain}`."
            print(f"OK, did not find `{must_not_contain}`.")
