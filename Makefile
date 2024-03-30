YELLOW=\033[1;33m
RESET=\033[0m

.PHONY: all generate solve clean
# 1 a 22 = Test
F = 22
P = 1

FILES = $(sort $(wildcard ./instances/*.txt))
FILE = $(word $(F), $(FILES))
BASENAME = $(basename $(notdir $(FILE)))

LPNAME = $(BASENAME)_$(P).lp
OUTNAME = $(BASENAME)_$(P).sol
all: main solve

main:
	@echo "$(YELLOW)Generating ...$(RESET)"
	cd src && python3 generate_model.py .$(FILE) $(P)
solve:
	@echo "$(YELLOW)Solving ...$(RESET)"
	glpsol --lp $(LPNAME) -o $(OUTNAME)
clean:
	@echo "$(YELLOW)Cleaning ...$(RESET)"
	@rm -f *.lp *.sol
