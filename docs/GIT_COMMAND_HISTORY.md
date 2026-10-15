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

## Documentation, merge and verified remote publication

The following commands also completed successfully on 15 October 2026. The first push attempt failed for missing authentication; a subsequent browser sign-in through Git Credential Manager resolved it. No credentials are included here.

```powershell
git remote add origin https://github.com/Welt-Tao/ProjectPos_2026.git
git add README.md START_POS.cmd docs
git commit -m 'Document UML design, runnable setup and presentation workflow'
git switch main
git merge --no-ff taoliyuan/development -m 'Merge verified individual POS implementation and documentation'
git push -u origin main taoliyuan/development
git ls-remote --heads origin
```

Final package refinements and artifact additions follow in the live repository history. The saved log is an evidence snapshot before the final packaging commit, not a claim to contain its own commit.
