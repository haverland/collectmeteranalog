# Changelog

## [1.1.0]

### Added
- Collect: Implement adjustable image collection root path
  - New parameter: `--collectpath`
- Label: Add possibilty to define the labeled images root folder working with label file
  - Define `--labeling` and `--labelfile` at the same time using different paths
- Label: Support label file with prediction data (modern csv file syntax)
  - Label file with legacy syntax (only index, file path) is still supported
- Label: Show prediction value parsed from label file
  - Precondition: Label file with modern syntax + No model selected
- App: Implement application version handling
  - Source of version: `collectmeteranalog/__version__.py`
  - New parameter `--version`
  - Automatically inject version to all build processes and GUI (window title)
  - Use version in github actions for artifacts

### Changed
- Collect: Fix image download counter
- Collect: Fix `keepdownloads` option - do not delete `images_raw` content
- Collect: Save downloaded JPG images without decode/encode to preserve original quality
- Collect: Refactor / streamline `readimages` function
- Label: Refactor functions for model prediction (`load_interpreter`, `predict`)
- Label: Refactor GUI button alignment / size
- App: Fix exit(1) - unknown error
- App: Refactored readme
- App: Updated github actions

### Removed
- Label: Internal model removed -> default: No model is used
- App: Repo cleanup


## [1.0.14]

- Fix OS downloads


## [1.0.8]

- fix failure in labeling with csv-file if multiple images are not available


## [1.0.1] - 2022-09-18

### Added

### Changed

- changed release action
- fixed requirements

### Removed
