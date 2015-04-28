#!/usr/bin/python

# College football computer ranker

# TODO: Faster

# Layout of teams data structure:
# Top level is hash table where the keys are team names, and the values are
# arrays
# Each array is made up of arrays, each of which is an individual "game"
# The layout of "game" arrays is:
# [result (W/L), opponent, team score, opponent score, location (H/A)]

import sys
import csv
import random
import math
import constants


def human_readable_cmps(weight):
	if weight == constants.hth_cmp_weight:
		return "Head to head"
	elif weight >= constants.co_base_cmp_weight:
		return "Common Opponents record"
	elif weight == constants.ffw_cmp_weight:
		return "Four fewer wins"
	elif weight == constants.aamco_14_cmp_weight:
		return "AAMCO >= 14"
	elif weight == constants.aamco_7_cmp_weight:
		return "AAMCO >= 7"
	elif weight == constants.wwabw_cmp_weight:
		return "WWABW"
	elif weight == constants.wabw_cmp_weight:
		return "WABW"
	elif weight == constants.or_cmp_weight:
		return "Overall record"
	elif weight == constants.or_tiebreaker_cmp_weight:
		return "Overall record h/a tiebreaker"
	elif weight == constants.aamov_cmp_weight:
		return "AAMOV"
	elif weight == constants.mw_cmp_weight:
		return "More wins"
	elif weight == constants.tie_cmp_weight:
		return "tie"
	else:
		return "ERROR: Bad input"


# Compares two teams, and returns True if t1 is better and False if t2 is
#  better.  The second element of the tuple returned is a weight of how
# important the distinction is
def cmp_teams(teams, prev_year_recs, t1, t2):
	# Head to head.  Assumes teams play each other no more than twice
	t1_won = False
	t2_won = False
	for game in teams[t1]:
		if (game[1] == t2):
			if game[0] == "W":
				t1_won = True
			else:
				t2_won = True
	if t1_won and not t2_won:
		return (True, constants.hth_cmp_weight)
	elif t2_won and not t1_won:
		return (False, constants.hth_cmp_weight)
	else:
		pass

	# Record against common opponents
	team1_opps = [game[1] for game in teams[t1]]
	team2_opps = [game[1] for game in teams[t2]]
	common_opps = [team for team in team1_opps if team in team2_opps]

	team1_common_opp_wins, _, t1_homecount, _ = record_vs_opp_set(teams, t1, common_opps)
	team2_common_opp_wins, _, t2_homecount, _ = record_vs_opp_set(teams, t2, common_opps)
	if team1_common_opp_wins > team2_common_opp_wins:
		return (True, constants.co_base_cmp_weight+2*len(common_opps))
	elif team2_common_opp_wins > team1_common_opp_wins:
		return (False, constants.co_base_cmp_weight+2*len(common_opps))
	else:
		# eliminating home/away tiebreak for now.  Maybe later it
		# can be inserted as a lower priority decision
		pass

	# Some setup for the rest
	(t1_wins, t1_losses, t1_h, t1_a) = record_vs_opp_set(teams, t1, team1_opps)
	(t2_wins, t2_losses, t2_h, t2_a) = record_vs_opp_set(teams, t2, team2_opps)

	# Short-circuit if one team has won four fewer games.  This is to get
	# rid of FCS teams who only play an FBS team once or twice and win them all
	if t1_wins > t2_wins + 3:
		return (True, constants.ffw_cmp_weight)
	elif t2_wins > t1_wins + 3:
		return (False, constants.ffw_cmp_weight)

	# AAMOV against common opponents
	aamco1 = avg_adjusted_mov_oppset(teams, t1, common_opps)
	aamco2 = avg_adjusted_mov_oppset(teams, t2, common_opps)

	# abs(aamco1 - aamco2) can never be greater than 20 if both teams have identical records
	if abs(aamco1 - aamco2) >= 14:
		return ((aamco1 > aamco2), constants.aamco_14_cmp_weight)
	elif abs(aamco1 - aamco2) >= 7:
		return ((aamco1 > aamco2), constants.aamco_7_cmp_weight)
	# If the aamcos are within 7, it's too close, lets move on to other factors

	# Best wins weighted by aamov
	wabw1 = weighted_average_best_wins(teams, prev_year_recs, t1)
	wabw2 = weighted_average_best_wins(teams, prev_year_recs, t2)
	aam1 = avg_adjusted_mov(teams, t1)
	aam2 = avg_adjusted_mov(teams, t2)

	# aams are on a -21 to 21 scale.  Normalize
	naam1 = (aam1 + 21)/42
	naam2 = (aam2 + 21)/42

	wwabw1 = (wabw1 * naam1*constants.mov_weight) + (wabw1 * constants.wins_weight)
	wwabw2 = (wabw2 * naam2*constants.mov_weight) + (wabw2 * constants.wins_weight)

	if wwabw1 > wwabw2:
		return (True, constants.wwabw_cmp_weight)
	elif wwabw2 > wwabw1:
		return (False, constants.wwabw_cmp_weight)
	else:
		pass

	if wabw1 > wabw2:
		return (True, constants.wabw_cmp_weight)
	elif wabw2 > wabw1:
		return (False, constants.wabw_cmp_weight)
	else:
		pass

	# Overall record
	t1_percent = t1_wins/(t1_wins+t1_losses)
	t2_percent = t2_wins/(t2_wins+t2_losses)
	if t1_percent > t2_percent:
		return (True, constants.or_cmp_weight)
	elif t2_percent > t1_percent:
		return (False, constants.or_cmp_weight)
	else:
		# tiebreak on home vs away
		if t1_a > t2_a:
			return (True, constants.or_tiebreaker_cmp_weight)
		elif t2_a > t1_a:
			return (False, constants.or_tiebreaker_cmp_weight)
		else:
			pass

	# average adjusted margin of victory
	if aam1 > aam2:
		return (True, constants.aamov_cmp_weight)
	elif aam2 > aam1:
		return (False, constants.aamov_cmp_weight)
	else:
		pass

	# More wins are better
	if t1_wins > t2_wins:
		return (True, constants.mw_cmp_weight)
	elif t2_wins > t1_wins:
		return (False, constants.mw_cmp_weight)
	else:
		pass

	# I give up, these teams are identical
	return (None, constants.tie_cmp_weight)


# For a set of opponents, what is a teams record against them
def record_vs_opp_set(teams, team, opps):
	wins = 0.0
	losses = 0.0
	home_count = 0.0
	away_count = 0.0
	for game in teams[team]:
		if game[1] in opps:
			if game[0] == "W":
				wins += 1
			else:
				losses += 1
			if game[4] == "A":
				away_count += 1
			else:
				home_count += 1
	return (wins, losses, home_count, away_count)


def calculate_wabw_team_wins(teams, prev_year_recs, team, opps, mod_weight):
	w, l, _, _ = record_vs_opp_set(teams, team, opps)
	res = w
	if constants.current_week < 5:
		# Adjust win counts by weighted average with previous year win counts
		if team in prev_year_recs.keys():
			res = res * (1.0 - mod_weight) + (prev_year_recs[team] * mod_weight)
		else:
			# If the opponent isn't in the prev_year_recs hash table,
			# they didn't play any games last year
			res = res * (1.0 - mod_weight)
	return res


# Calculates the weighted average of the number of wins of the three highest
# win total win of a given team.  Uses the formula:
# (3*best_win + 2*second_best_win + third_best_win)/6
def weighted_average_best_wins(teams, prev_year_recs, team):
	if "team_wins" not in weighted_average_best_wins.__dict__:
		weighted_average_best_wins.team_wins = {}

	opp_wins = []

	if constants.current_week < 5:
		# Modify the wins by the win totals last year
		# week 1 - 100%, week 2 - 75%, week 3 - 50%, week 4: 25%
		mod_weight = (float(5-constants.current_week))/4
	else:
		mod_weight = 0

	for game in teams[team]:
		if game[0] == "W":
			if not game[1] in weighted_average_best_wins.team_wins.keys():
				weighted_average_best_wins.team_wins[game[1]] = calculate_wabw_team_wins(
					teams,
					prev_year_recs,
					game[1],
					teams.keys(),
					mod_weight)
			opp_wins.append(weighted_average_best_wins.team_wins[game[1]])

	opp_wins.sort(reverse=True)
	if len(opp_wins) >= 3:
		return (3*opp_wins[0] + 2*opp_wins[1] + opp_wins[2])/6
	else:
		tot_wins = 0
		weight = 3
		for i in opp_wins:
			tot_wins += weight*i
			weight -= 1
		if len(opp_wins) == 2:
			return tot_wins/5
		else:
			return tot_wins/3


# Calculates the average margin of victory over all games, but setting all
# totals above 21 to 21 because there really isn't much of a difference after
# a 3 TD lead and we don't want to reward running up the score
def avg_adjusted_mov(teams, team):
	num_games = 0.0
	total_margin = 0.0
	for game in teams[team]:
		margin = game[2]-game[3]
		if abs(margin) > constants.max_mov:
			if margin > 0:
				margin = constants.max_mov
			else:
				margin = -constants.max_mov
		num_games += 1
		total_margin += margin
	return total_margin / num_games


def avg_adjusted_mov_oppset(teams, team, opps):
	num_games = 0.0
	total_margin = 0.0
	for game in teams[team]:
		if game[1] in opps:
			margin = game[2]-game[3]
			if abs(margin) > constants.max_mov:
				if margin > 0:
					margin = constants.max_mov
				else:
					margin = -constants.max_mov
			num_games += 1
			total_margin += margin
	if num_games > 0:
		return total_margin / num_games
	else:
		# All teams call into this function regardless of whether they have
		# common games
		# Returning 0 means that they have the same AAM against their
		# empty set of common opponents
		return 0


# What is the quality of a given team ordering?  Lower is better
def order_quality(teams_arr, teamcmps):
	quality = 0
	i = 0
	j = 1
	for team1 in teams_arr:
		for team2 in teams_arr[i:]:
			diff, weight = teamcmps[(team2, team1)]
			if diff:
				quality += weight*(j-i)
			j += 1
		i += 1
		j = i+1
	return quality


# Iteratively order the teams given an initial order.  Python doesn't optimize tail recursion
# which makes me extremely unhappy
def order_teams(team_order, teamcmps):
	misses = 0
	num_teams = len(team_order)
	num_misses_to_continue = (num_teams/2) * (num_teams + 1)  # == 1+...+num_teams
	k = 0
	initial_quality = order_quality(team_order, teamcmps)
	switch_cache = set()
	while (k < constants.max_iterations) and (misses < num_misses_to_continue):
		condition = True
		while condition:
			i = random.randint(0, num_teams-1)
			j = random.randint(0, num_teams-1)
			condition = (i, j) in switch_cache
		switch_cache.add((i, j))
		switch_cache.add((j, i))
		team_order[i], team_order[j] = team_order[j], team_order[i]
		new_quality = order_quality(team_order, teamcmps)
		if (new_quality >= initial_quality):
			# Didn't help :(
			team_order[i], team_order[j] = team_order[j], team_order[i]
			misses += 1
		else:
			# Only overwrite if we changed something
			initial_quality = new_quality
			misses = 1  # We won't be retrying the previous ordering, so count that as a miss
			k += 1
			switch_cache.clear()
			# Don't retry the ordering we just did
			switch_cache.add((i, j))
			switch_cache.add((j, i))
	print("Ordered teams:\n\tMisses: %d\n\tIterations: %d\n\tQuality: %d"
	      % (misses, k, initial_quality))
	return team_order


# Loads a hash table with last years team names and win counts
def load_prev_year_records():
	f = open(constants.prev_year_data_file, "rb")
	reader = csv.reader(f)
	res = {}
	rownum = 0
	for row in reader:
		if rownum == 0:
			next
		else:
			if (row[tsh_col] == ' ' or row[tsh_col] == ''
			    or row[tsv_col] == ' ' or row[tsv_col] == ''):
				continue
			if (int(row[tsv_col]) > int(row[tsh_col])):
				# Visitor won
				if (not row[tnv_col] in res.keys()):
					res[row[tnv_col]] = 0
				res[row[tnv_col]] += 1
			else:
				# Home won
				if (not row[tnh_col] in res.keys()):
					res[row[tnh_col]] = 0
				res[row[tnh_col]] += 1
		rownum += 1
	return res

if __name__ == '__main__':

	random.seed()

	f = open(constants.infile, "r")
	reader = csv.reader(f)

	teams = {}

	rownum = 0
	for row in reader:
		if rownum == 0:
			next
		else:
			if (row[constants.tsh_col] == ' ' or row[constants.tsh_col] == ''
					or row[constants.tsv_col] == ' ' or row[constants.tsv_col] == ''):
				continue
			visitorname = row[constants.tnv_col]
			homename = row[constants.tnh_col]
			visitorscore = int(row[constants.tsv_col])
			homescore = int(row[constants.tsh_col])

			if (visitorname not in teams.keys()):
				teams[visitorname] = []
			if (homename not in teams.keys()):
				teams[homename] = []

			teams[visitorname].append(["W" if (visitorscore > homescore) else "L"
						   , homename, visitorscore, homescore, "A"])
			teams[homename].append(["W" if (homescore > visitorscore) else "L"
						, visitorname, homescore, visitorscore, "H"])

		rownum += 1

	prev_year_recs = {}
	if constants.current_week < 5:
		# prev_year_recs is a hash table where the keys are team names and the
		# values are the number of wins they had last year
		prev_year_recs = load_prev_year_records()

	# Compare all teams
	teamcmps = {}

	metric_counts = {}
	total_cmps = 0

	for team1 in teams.keys():
		for team2 in teams.keys():
			teamcmps[(team1, team2)] = cmp_teams(teams, prev_year_recs, team1, team2)
			teamcmps[(team2, team1)] = cmp_teams(teams, prev_year_recs, team2, team1)
			# Count up how frequently each metric is used to determine the comparison
			weight = teamcmps[(team1, team2)][1]
			# Collapse "Common opps" to one point
			if (weight < constants.hth_cmp_weight and weight >= constants.co_base_cmp_weight):
				weight = constants.co_base_cmp_weight
			if weight in metric_counts:
				metric_counts[weight] += 1
			else:
				metric_counts[weight] = 1
			total_cmps += 1

	big_ten = ["Northwestern", "Wisconsin", "Michigan", "Indiana", "Purdue",
		"Illinois", "Maryland", "Rutgers", "Ohio State", "Minnesota", "Nebraska",
		"Michigan State", "Penn State", "Iowa"]

	if len(sys.argv) == 1:
		# Print out a ranking
		team_order = order_teams(list(teams.keys()), teamcmps)

		num = 0
		for team in team_order:
			num += 1
			if num > 30 and team not in big_ten:
				continue
			wins, losses, _, _ = record_vs_opp_set(teams, team, [game[1] for game in teams[team]])
			print("%d. %s (%d-%d)" % (num, team, wins, losses))

		# Print out the metrics used:
		print("\nMetrics:")
		for (metric, m_count) in metric_counts.items():
			print("%s: %0.2f%%" % (human_readable_cmps(metric), 100*float(m_count)/float(total_cmps)))

	elif len(sys.argv) == 2:
		if sys.argv[1] == "once":
			for (team, games) in teams.items():
				if (len(games) == 1):
					print(team)
		else:
			# Display info about the team
			for game in teams[sys.argv[1]]:
				w, l, _, _ = record_vs_opp_set(teams, game[1], teams)
				print("%s - %s: %d-%d" % (game[0], game[1], w, l))
			print("AAMOV: %f" % avg_adjusted_mov(teams, sys.argv[1]))
			print("WABW: %f" % weighted_average_best_wins(teams, prev_year_recs, sys.argv[1]))

	elif len(sys.argv) == 3:
		# Print the relative ranking between the teams and its weight (which gives you the reason)
		# If "all" is the second argument, display the first team vs all teams
		if sys.argv[2] == "all":
			for team in teams.keys():
				(val, weight) = teamcmps[(sys.argv[1], team)]
				print("%s - %s: %s" % (team, val, human_readable_cmps(weight)))

		else:
			(val, weight) = teamcmps[(sys.argv[1], sys.argv[2])]
			print((val, human_readable_cmps(weight)))
	else:
		# Print the quality of the given ordering
		for team in sys.argv[1:]:
			if team not in teams.keys():
				print("%s not found" % team)
		print(order_quality(sys.argv[1:]))
