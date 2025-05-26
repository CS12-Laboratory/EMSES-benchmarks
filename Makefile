EXPS := hole probe spacecraft

.DEFAULT_GOAL := exp_all

.PHONY: exp_all compare_all

exp_all: $(addprefix exp_,$(EXPS))

compare_all: $(addprefix compare_,$(EXPS))

exp_%:
	cd experiments/exp_$* && \
	mymkdir --key emses . && \
	preinp && \
	mysbatch job-camphor.sh

compare_%:
	python3 scripts/compare_gprof.py \
	  --dir results/exp_$* \
	  --out gprof_compare_$*.png \
	  --top 10
