.PHONY: setup

setup:  ## One-time setup after cloning: install deps, approve .envrc, and install git hooks
	uv sync
	@if ! command -v direnv >/dev/null 2>&1; then \
		echo ""; \
		echo "Note: direnv not found (optional, macOS/Linux only)."; \
		echo "  macOS:  brew install direnv"; \
		echo "  Linux:  sudo apt install direnv"; \
		echo "  Then add the shell hook: https://direnv.net/docs/hook.html"; \
		echo ""; \
	else \
		grep -q 'direnv hook' ~/.zshrc 2>/dev/null || grep -q 'direnv hook' ~/.bashrc 2>/dev/null || { \
			echo ""; \
			echo "Note: direnv is installed but not hooked into your shell."; \
			echo "Add one of the following to your shell rc file, then restart your shell:"; \
			echo "  ~/.zshrc:   eval \"\$$(direnv hook zsh)\""; \
			echo "  ~/.bashrc:  eval \"\$$(direnv hook bash)\""; \
			echo "  See: https://direnv.net/docs/hook.html"; \
			echo ""; \
		}; \
		direnv allow . || { \
			echo ""; \
			echo "Warning: 'direnv allow .' failed — run it manually after checking your .envrc."; \
			echo ""; \
		}; \
	fi
	uv run prek install --hook-type pre-commit --hook-type pre-push --hook-type post-checkout --overwrite
