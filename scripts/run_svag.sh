# Usage: bash scripts/run_svag.sh
#input_file=''

python3 run_svag.py # \
#--input_file ${input_file}

# Run spatial and temporal eval. Need to change their arguments in the files
sh  ../spatial_eval/evaluate.sh
sh ../temporal_eval/eval.sh