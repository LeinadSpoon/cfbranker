#!/usr/bin/python

prev_year_data_file = "cfb2013lines.csv"
current_week = 5  # No difference for weeks after week 5

infile = "cfb2014lines.csv"
tnv_col = 1
tnh_col = 3
tsv_col = 2
tsh_col = 4
max_mov = 21
max_iterations = 300000
mov_weight = 0.25
wins_weight = 0.75

# Comparison weightings
hth_cmp_weight = 30
co_base_cmp_weight = 10
ffw_cmp_weight = 7
aamco_14_cmp_weight = 6
aamco_7_cmp_weight = 5
wwabw_cmp_weight = 4
wabw_cmp_weight = 3
or_cmp_weight = 2
or_tiebreaker_cmp_weight = 1.5
aamov_cmp_weight = 1
mw_cmp_weight = 0.5
tie_cmp_weight = 0


