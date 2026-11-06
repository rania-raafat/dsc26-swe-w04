# AI usage

Keep all three headings exactly as they are. If this file is missing or any heading is
missing, the grader stops and gives 0 ("AI_USAGE.md missing or incomplete"). The content
is not scored, but your Track Mentor reads it and the W8 defence can ask about it.

## Tools

<!-- Which tools you used (ChatGPT, Copilot, Claude, Cursor, none...) and for which parts. -->
I used ChatGPT as an AI assistant during this task.
I used it to:
Understand the task requirements and the behavior described in SPEC.md.
Identify the important edge cases and the 13 targeted mutants.
Plan the unit, API, and contract test structure.
Get guidance on writing pytest tests and using FastAPI TestClient.
Review test failures and understand why each assertion is important.

## What AI got wrong

<!-- At least one thing an assistant got wrong that you changed, and how you noticed
(a test failed, the docs said otherwise, you ran it). -->
During the process, ChatGPT initially predicted that the API test folder would contain 10 tests and that the complete suite would have 26 tests. However, my actual pytest output showed 9 API tests and 27 tests overall at that stage.

I checked the test collection and terminal output and corrected the count. I relied on the actual test results rather than the AI's prediction.

## In my own words

<!-- Answer without AI, one or two sentences each. -->

1. Pick one mutant your first draft of tests did not kill. Why not, and what did you add?

My first draft focused on testing the business rules and the main API operations. It did not explicitly check whether the requestedAt timestamp contained timezone information, so it would not catch M08. I added a contract test that checks that the timestamp ends with Z and validates the response against the JSON Schema.

2. Why is a test that only asserts `status_code == 409` weaker than one that asserts the problem `type`?

Checking only status_code == 409 is weaker because different errors can have the same HTTP status code. For example, approving an already approved transfer and attempting a transfer that violates the reserve both return 409. Checking the problem type tells us exactly which error occurred and verifies that the API follows the expected specification.