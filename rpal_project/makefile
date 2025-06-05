# ---- Configuration ----
PYTHON=python
MAIN=myrpal.py
TEST_DIR=tests
FILES=$(wildcard $(TEST_DIR)/*.rpal)

# ---- Targets ----

# Run AST mode
ast:
	$(PYTHON) $(MAIN) -ast $(FILE)

# Run eval mode
run:
	$(PYTHON) $(MAIN) $(FILE)

# Run all test files (default mode: evaluation)
test:
	@for file in $(FILES); do \
		echo "Running: $$file"; \
		$(PYTHON) $(MAIN) $$file; \
		echo ""; \
	done

# Clean output or temp files (customize as needed)
clean:
	rm -f *.out *.tmp


# Declare these targets as always-run
.PHONY: ast run test clean