# Publishing the repository

The local repository already contains commit history. Uploading files individually through the website would lose that history. Publish the existing repository with Git or GitHub Desktop.

## Create the empty remote

Sign in to GitHub as `Welt-Tao`, choose New repository and name it `ProjectPos_2026`. Leave the README, .gitignore and license initialisation options unchecked because these files already exist locally. Choose visibility according to the course submission requirements. If private, grant your assessor access through the normal GitHub interface.

## Push the existing repository

Open a terminal in the `ProjectPos_2026` folder and run the commands below after the remote exists:

```powershell
git remote add origin https://github.com/Welt-Tao/ProjectPos_2026.git
git push -u origin main
git push -u origin taoliyuan/development
git ls-remote --heads origin
```

If `origin` already exists, inspect `git remote -v` and do not add it a second time. Complete any GitHub sign-in in the browser. Never paste your password or personal access token into chat or a file in the repository.

## GitHub Desktop alternative

In GitHub Desktop choose File, Add local repository, and select the `ProjectPos_2026` directory. Choose Publish repository, verify the owner and repository name, and publish. Switch to `taoliyuan/development` and publish that branch as well. Do not delete either branch.

## Evidence

Verify that the remote shows both branches and the commit history. Save the final command output with:

```powershell
git log --all --graph --decorate --date=iso-strict > docs/git-log.txt
git ls-remote --heads origin > docs/remote-branches.txt
```

The final report must contain a verified repository URL. A planned URL does not prove that the repository has been published.
