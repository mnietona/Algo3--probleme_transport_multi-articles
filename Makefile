YELLOW=\033[1;33m
RESET=\033[0m

.PHONY: all generate solve clean
# 1 a 22 = Test
F = 22
P = 0

FILES = $(sort $(wildcard instances/*.txt))
FILE = $(word $(F), $(FILES))
BASENAME = $(basename $(notdir $(FILE)))

LPNAME = $(BASENAME)_$(P).lp
OUTNAME = $(BASENAME)_$(P).sol
all: main solve

main:
	@echo "$(YELLOW)Generating ...$(RESET)"
	python3 generate_model.py $(FILE) $(P)
solve:
	@echo "$(YELLOW)Solving ...$(RESET)"
	glpsol --lp $(LPNAME) -o $(OUTNAME)
clean:
	@echo "$(YELLOW)Cleaning ...$(RESET)"
	@rm -f *.lp *.sol; find . -type d -name __pycache__ -exec rm -r {} \+; find . -type d -name .pytest_cache -exec rm -r {} \+
