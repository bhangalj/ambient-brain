---
description: Route a dictated brain-dump into the work brain
---
Take everything in $ARGUMENTS (a dictated work brain-dump) and route it into the
vault by running:

```
echo "$ARGUMENTS" | python scripts/braindump_router.py
```

Then briefly confirm to me what went where. If a referenced project doesn't exist
yet, create its folder + _project.md from templates/project.md first.
