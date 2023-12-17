USE_CONDA ?= 1
INSTALL_SCRIPT = install_with_conda.sh
ifeq (false,$(USE_CONDA))
	INSTALL_SCRIPT = install_with_venv.sh
endif

# help: help					- Display this makefile's help information
.PHONY: help
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

# help: install					- Create a virtual environment and install dependencies
.PHONY: install
install:
	@bash bin/$(INSTALL_SCRIPT)

# help: install_precommit			- Install pre-commit hooks
.PHONY: install_precommit
install_precommit:
	@pre-commit install -t pre-commit
	@pre-commit install -t pre-push

# help: format_code				- Run pre-commit on all files
.PHONY: format_code
format_code:
	@pre-commit run -a
