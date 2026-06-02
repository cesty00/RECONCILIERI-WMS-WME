# PR Creation Read-Back Guard

Required repository:
cesty00/RECONCILIERI-WMS-WME

Repository id:
1257065922

Rule:
After creating any branch, commit, or Pull Request, the agent must verify the object by reading it back from GitHub in the required repository.

A task may report READY_FOR_REVIEW only if all are true:

- repository routing still returns cesty00/RECONCILIERI-WMS-WME
- repository id still returns 1257065922
- branch exists in branch list
- commit exists on that branch
- PR exists and can be fetched by PR number
- PR base branch is main
- PR head branch is the expected branch
- PR changed files match expected scope

If any read-back verification fails:

- do not report READY_FOR_REVIEW
- report BLOCKED
- include the failed object, e.g. PR_NOT_FOUND, BRANCH_NOT_FOUND, COMMIT_NOT_FOUND

Future task report must include:

- Branch read-back verified: YES / NO
- Commit read-back verified: YES / NO
- PR read-back verified: YES / NO
- PR changed files verified: YES / NO
