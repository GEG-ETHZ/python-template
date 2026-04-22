.PHONY: setup

setup:  ## Optional: approve .envrc so direnv auto-activates your environment on cd
	@if ! command -v direnv >/dev/null 2>&1; then \
		echo "direnv not found. Install it first:"; \
		echo "  macOS:  brew install direnv"; \
		echo "  Linux:  sudo apt install direnv"; \
		echo "  Then add the shell hook: https://direnv.net/docs/hook.html"; \
		exit 1; \
	fi
	@grep -q 'direnv hook' ~/.zshrc 2>/dev/null || grep -q 'direnv hook' ~/.bashrc 2>/dev/null || { \
		echo ""; \
		echo "direnv is installed but not hooked into your shell."; \
		echo "Add one of the following (as appropriate) to your shell rc file and restart your shell:"; \
		echo "  ~/.zshrc:   eval \"\$$(direnv hook zsh)\""; \
		echo "  ~/.bashrc:  eval \"\$$(direnv hook bash)\""; \
		echo "See: https://direnv.net/docs/hook.html"; \
		echo ""; \
	}
	direnv allow .
