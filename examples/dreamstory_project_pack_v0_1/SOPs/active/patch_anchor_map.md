# SOP: Patch Anchor Map

## Trigger

Any source patch or script delivery that changes project files.

## Required process

1. Confirm project root, Assets, git status, target files, encoding, and line endings.
2. Confirm current target method structure.
3. Produce anchor map before patch script.
4. Avoid long brittle multi-line anchors.
5. Include restore behavior and failure stop.

## Stop conditions

- Missing current target content.
- Missing anchor map.
- Dirty state not accounted for.
