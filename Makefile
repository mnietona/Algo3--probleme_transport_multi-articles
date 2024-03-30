.DEFAULT_GOAL := main
# 1 a 22
FILE_INDEX = 4
FILES = $(sort $(wildcard ./instances/*.txt))
FILE = $(word $(FILE_INDEX), $(FILES))

AGREE = 0

BASENAME = $(basename $(notdir $(FILE)))

LPNAME = $(BASENAME)_0.lp
OUTNAME = $(BASENAME)_0.sol

main:
	cd src && python3 generate_model.py .$(FILE) $(AGREE)

test:
	glpsol --lp $(LPNAME) -o $(OUTNAME)