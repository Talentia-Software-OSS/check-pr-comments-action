# Check Pull Request comments github action

This action helps to enforce some conventions in pull requests comments. It can check that comments do include some
piece of text or that it does *not* include another piece of text.

This can be useful in conjunction
with [PR comment template](https://docs.github.com/en/free-pro-team@latest/github/building-a-strong-community/creating-a-pull-request-template-for-your-repository)
, using this action to make sure that PR author did not forget to replace placeholder text with real info.

## Inputs

### `comments-must-contain`

Check that the given text appears in pull request body.

### `comments-must-not-contain`

Check that the given text does not appear at all in pull request body.

## Outputs

None.

## Example usage

    - name: Check Pull Request comments
      uses: actions/CheckPRComments@v0
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Required to to act on pull request through GitHub API 
      with:
        comments-must-contain: '# Description'
        comments-must-not-contain: '- [ ]'
