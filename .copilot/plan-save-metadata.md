## Plan: Save Recent Wikimedia Attribution Metadata

Add attribution sidecar generation to the existing Wikimedia scraper without introducing image downloads. The scraper will retain the API's full `extmetadata`, select the three newest successfully fetched results by parsed upload timestamp, and write one UTF-8 `.txt` sidecar per selected image into a dedicated configurable directory.

**Steps**
1. Extend configuration defaults and validation in `Plan - exercise-2/wikimedia-scraper/config_validator.py` with a `metadata_output_dir` option, defaulting to `metadata`, and require it to be a non-empty string when supplied. Update `config.yaml` and the sample `test_file_config.yaml` as appropriate so the behavior is discoverable while preserving existing configs.
2. Preserve attribution data in `WikimediaScraper._fetch_images` in `Plan - exercise-2/wikimedia-scraper/wikimedia_scraper.py` by storing the complete `extmetadata` mapping on each image result, while keeping the existing aggregate output fields and description extraction intact.
3. Add focused scraper helpers in `wikimedia_scraper.py` to parse timestamps, select at most three newest valid results deterministically, derive a safe exact-stem sidecar filename from a Wikimedia title (remove the `File:` prefix, retain the image stem, and use `.txt`), and write the attribution content. Each file must begin exactly with `Attribution metadata for <image name>`; include the available metadata fields in a stable readable key/value format, and create the configured directory before writing.
4. Integrate sidecar writing into `WikimediaScraper.run()` after fetching images and before/alongside aggregate output. Metadata generation should happen for zero to three available images, avoid crashing on missing or malformed optional metadata, and let genuine filesystem/API failures follow the existing error handling path. Use the configured metadata directory rather than coupling sidecars to `output_file`.
5. Add unit tests under `Plan - exercise-2/wikimedia-scraper/tests/` for: retaining extmetadata, selecting three newest files and handling fewer than three, stable behavior for malformed/missing timestamps, exact-stem filename conversion including `File:` titles, required attribution header and representative metadata output, directory creation, and the configured path being honored. Extend config tests for the new default and validation.
6. Update `Plan - exercise-2/wikimedia-scraper/README.md` to document the new option, default directory, selection rule, filename convention, and metadata output format. Clarify that this feature writes attribution sidecars for scraped results and does not download image binaries.

**Relevant files**
- `/Users/saurabhbhatia/Documents/GitHub/github-copilot-training-lab/Plan - exercise-2/wikimedia-scraper/wikimedia_scraper.py` - owning orchestration and API-to-result transformation; extend `_fetch_images`, `run`, and small focused helpers.
- `/Users/saurabhbhatia/Documents/GitHub/github-copilot-training-lab/Plan - exercise-2/wikimedia-scraper/config_validator.py` - add and validate `metadata_output_dir`.
- `/Users/saurabhbhatia/Documents/GitHub/github-copilot-training-lab/Plan - exercise-2/wikimedia-scraper/output_formatter.py` - reuse `write_to_file` for UTF-8 sidecar writes if its contract is sufficient; otherwise make only the minimal encoding adjustment and cover it.
- `/Users/saurabhbhatia/Documents/GitHub/github-copilot-training-lab/Plan - exercise-2/wikimedia-scraper/config.yaml` - show the new setting.
- `/Users/saurabhbhatia/Documents/GitHub/github-copilot-training-lab/Plan - exercise-2/wikimedia-scraper/test_file_config.yaml` - keep the sample file representative of the supported config.
- `/Users/saurabhbhatia/Documents/GitHub/github-copilot-training-lab/Plan - exercise-2/wikimedia-scraper/tests/test_config_validator.py` - add default/type/value coverage.
- `/Users/saurabhbhatia/Documents/GitHub/github-copilot-training-lab/Plan - exercise-2/wikimedia-scraper/tests/` - add scraper-focused tests using mocked API responses and temporary directories; do not make live Wikimedia requests.
- `/Users/saurabhbhatia/Documents/GitHub/github-copilot-training-lab/Plan - exercise-2/wikimedia-scraper/README.md` - document configuration and output behavior.

**Verification**
1. Run the focused unittest module(s) for the scraper metadata behavior from `Plan - exercise-2/wikimedia-scraper` with the project virtual environment/dependencies available.
2. Run `python -m unittest discover -s tests` from that directory to confirm existing config behavior remains intact.
3. Exercise a mocked or deterministic temporary-directory run with five out-of-order image timestamps and verify exactly three sidecars, newest-first selection independent of API order, required first line, matching stems, and no sidecars beyond the three selected.
4. Run a syntax/diagnostic check on modified Python files and inspect the final diff for scope, especially that no image download or unrelated refactor was introduced.

**Decisions**
- “Along with the image” means attribution files for the image results already scraped; binary image downloading is explicitly out of scope.
- Sidecars use a dedicated `metadata_output_dir` configuration option, default `metadata`, and are not inferred from `output_file`.
- “Three most recent” means timestamp sorting, not trusting search result order. Valid ISO timestamps are compared as timezone-aware datetimes; malformed or missing timestamps are handled deterministically and do not displace valid recent results.
- Filename convention is the image title's stem after removing the Wikimedia `File:` prefix, with `.txt` replacing the image extension. Because titles can contain path separators or other unsafe characters, the implementation must prevent path traversal while preserving the requested stem convention as far as filesystem-safe naming allows.
- Existing aggregate output remains unchanged.

**Further Considerations**
1. Metadata values may contain HTML or nested dictionaries from Wikimedia. Prefer a stable serializer that preserves attribution information without unsafe evaluation or nondeterministic Python repr output; avoid silently dropping fields.
2. If no valid timestamp exists, the plan should define a deterministic fallback (original result order) so behavior remains testable while valid timestamps always rank ahead of invalid ones.
