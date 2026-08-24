# Copilot instructions for this repository

## Repository summary

This repository is currently a minimal GitHub training workspace rather than a production application. As of the current state, it contains only Git metadata and a GitHub configuration directory; there are no application source files, dependency manifests, tests, build scripts, or CI workflows.

This means the repo does not currently define a language, framework, runtime, or build system. Treat this as a blank or intentionally empty project until additional files are added. Do not assume Node.js, Python, Java, .NET, Go, Ruby, or any other stack is present unless a manifest or source file proves it.

## High-level project facts

- Repo size: extremely small / empty repository
- Project type: training / lab repo, not an application codebase yet
- Languages/frameworks/runtime: none detected at present
- Build system: none configured
- Tests: none configured
- CI/CD: none configured
- Documentation: none present beyond this instruction file

## Repository layout

Current root contents:

- .git/ - Git metadata
- .github/ - GitHub-specific config
- .github/copilot-instructions.md - this file

No README.md, package.json, pyproject.toml, requirements.txt, Cargo.toml, go.mod, Dockerfile, Makefile, .github/workflows/, src/, app/, tests/, or other project directories are present.

The repository is effectively empty. Any future addition of source files and manifests should be treated as the source of truth; this instruction file should be updated if the repo becomes a real project.

## Build, validate, and run guidance

Do not run speculative build commands in this repo. There is no configured project to bootstrap, build, test, lint, or run.

Validated repository state:

```bash
cd <repo-root>
ls -la
find . -maxdepth 3 -type f | sort
git --no-pager status --short --branch
```

These commands complete successfully and confirm there are no project files to build or validate.

### Required workflow when the repo is empty

1. Start by confirming whether the repository actually contains a project manifest or source files.
2. If no source files or manifests exist, do not invent a build pipeline.
3. Only add or run project commands after a concrete manifest or stack is introduced.
4. If you are asked to scaffold a new project, prefer the simplest standard setup for the chosen language and then document the exact commands in this file.

### Commands that should not be used here

Do not run commands such as:

- npm install
- npm test
- pytest
- cargo build
- go test ./...
- mvn test
- dotnet test
- make
- docker build
- any framework-specific generator without a clear project requirement

These commands are not valid for the current repository state and would only create noise or fail due to missing configuration.

## CI and validation expectations

There is no GitHub Actions or other pipeline configured in this repository right now. There are no checks to mirror locally.

When the repository later gains a real project, the following should be added to the instructions:

- exact bootstrap steps
- exact install steps
- exact build commands
- exact test commands
- exact lint commands
- required environment versions (Node, Python, Java, etc.)
- any ordering requirements such as install before build
- any necessary cleanup steps

Until then, the correct behavior is to avoid creating synthetic validation steps that do not correspond to a working project.

## Working rules for Copilot agents

- Trust this file first. It reflects the repository state as it exists now.
- Only perform a search if the information here is incomplete or contradicts the repository state.
- Do not assume a stack exists without verifying a manifest or source file.
- Do not add build or test automation for a project that does not exist.
- Keep changes minimal and consistent with the repository’s actual contents.
- If future project files are added, update this instruction file to describe the real stack, layout, and commands.

## Practical guidance for future development

If this repository is later populated with a project, the instructions should be expanded to include:

- repository summary and purpose
- language/framework/runtime details
- root directory listing and structural overview
- key source directories and files
- configuration files for linting, formatting, and testing
- bootstrap and install steps
- build, test, lint, and run commands in the correct order
- CI workflow expectations and validation checks
- any known workarounds, environment requirements, or timing caveats

For the current empty repository, the correct action is simply to avoid unnecessary exploration and to respect the fact that there is no buildable project here yet.
