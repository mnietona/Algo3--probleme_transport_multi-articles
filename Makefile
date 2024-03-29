.DEFAULT_GOAL := main

PROUT = ../instances/test.txt
AGREE = 0

main:
	cd src && python3 generate_model.py ../instances/20_2_nonvalidly.txt 0

run:
	cd src && python3 generate_model.py $(PROUT) $(AGREE)
	