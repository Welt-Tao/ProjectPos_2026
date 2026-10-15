# Git command history

These commands were actually executed for this local individual repository on 15 October 2026. Repeated inspection commands are omitted. Commands are not backdated and no separate team members are invented.

```powershell
git init -b main
git config user.name 'Taoliyuan'
git config user.email 'welt799@163.com'
git add PROJECT_PLAN.md .gitignore
git commit -m 'Plan individual POS scope and acceptance criteria'
git switch -c taoliyuan/development
git add app.py pos static
git commit -m 'Implement atomic cash sales, receipt returns and English POS interface'
git add tests START_POS.cmd docs/screenshots
git commit -m 'Verify sale and return workflows with 22 tests and browser evidence'
git log --format='%h %ad %s' --date=iso-strict
```

Commit identities identify the project owner. AI assistance supported implementation and artifact preparation, and the student must review and understand the work before submission. Remote publishing commands are documented separately and become completed evidence only after a successful push.
