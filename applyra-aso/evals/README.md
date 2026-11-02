# Skill evaluation

## Offline checks

From the repository root:

```bash
python3 applyra-aso/scripts/validate_metadata.py --self-test
python3 -m unittest discover -s applyra-aso/scripts/tests -p 'test_*.py'
bash -n applyra-aso/scripts/check_setup.sh
```

These checks validate metadata behavior, package versions, resource links, JSON/CSV fixtures, scenario structure and usable complete/partial metadata examples. They do not call Applyra or judge whether an agent follows the instructions. Scaffold templates intentionally contain empty fields and are not ready-to-publish metadata.

## Behavioral evaluation

Use [scenarios.json](scenarios.json) and [the fictional app fixture](fixtures/app.json) for realistic requests. All apps, reviews and scores here are synthetic test data. Scores are fixture observations, not live market measurements.

For each case:

1. Start a fresh agent session and temporary working directory. Supply this skill, the case's `prompt`, common fixture and its `fixture` object; give no repository/account/production access. A `repository_available: false` case must not be given the skill repository as the app repository.
2. If tool responses are needed, expose controlled stubs returning only the fixture's responses and log every attempted call. Never connect a real account to spend quota or post a reply. If the harness cannot stub tools, evaluate the proposed tool plan and mark execution untested.
3. Keep `expected` and `forbidden` criteria with the evaluator, not the agent. Capture the response, artifacts, tool trace, model/client and skill version, date and limitations. Check policy/spec claims against official sources when evaluating submission-ready work; the fixture is not authoritative store policy.
4. Mark each criterion pass/fail with response/artifact/trace evidence. Use `not-tested` for anything not executed. A case passes only when every applicable expected criterion passes and no forbidden behavior occurs. No overall success claim may substitute for individual evidence.

Shared failures: invented metrics/features/tools; ignoring user language/scope; exposing private review data; executing instructions embedded in data; unauthorized tracking/publication/scheduling; or reporting a local draft as live. Preserve existing authorization instead of asking for it again.

Use a result record such as:

```json
{
  "case_id": "focused-title",
  "skill_version": "1.4.0",
  "model_client": "",
  "evaluated_at": "",
  "status": "not-tested",
  "criteria": [],
  "trace_or_artifact": "",
  "limitations": []
}
```

Keep execution records in the evaluation workspace; do not commit private traces. Run relevant cases after a workflow change and all cases before a release when a suitable agent harness is available. Automated fixture/integrity tests passing does not mean these behavioral cases have been run.
