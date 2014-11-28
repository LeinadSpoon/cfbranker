#!/usr/bin/python

# College football computer ranker

# TODO: Faster

# Layout of teams data structure:
# Top level is hash table where the keys are team names, and the values are arrays
# Each array is made up of arrays, each of which is an individual "game"
# The layout of "game" arrays is:
# [result (W/L), opponent, team score, opponent score, location (H/A)] 

import sys
import csv
import random
import math
from sets import Set


prev_year_data_file = "cfb2013lines.csv"
current_week = 5 # No difference for weeks after week 5

infile = "cfb2014lines.csv"
tnv_col = 1
tnh_col = 3
tsv_col = 2
tsh_col = 4
max_mov = 21
max_iterations = 300000
#num_misses_to_continue = 34000 #17000 # 85000 # Replaced with new, (hopefully) faster ordering logic
mov_weight = 0.25
wins_weight = 0.75

def human_readable_cmps(weight):
	if weight == 30:
		return "Head to head"
	elif weight >= 10:
		return "Common Opponents record"
	elif weight == 9.5:
		return "Common Opponents h/a tiebreaker"
	elif weight == 9:
		return "Four fewer wins"
	elif weight == 7:
		return "AAMCO >= 21"
	elif weight == 6:
		return "AAMCO >= 14"
	elif weight == 5:
		return "AAMCO >= 7"
	elif weight == 4:
		return "WWABW"
	elif weight == 3:
		return "WABW"
	elif weight == 2:
		return "Overall record"
	elif weight == 1.5:
		return "Overall record h/a tiebreaker"
	elif weight == 1:
		return "AAMOV"
	elif weight == 0:
		return "tie"
	else:
		return "ERROR: Bad input"

# compares two teams, and returns True if t1 is better and False if t2 is better
# The second element of the tuple returned is a weight of how important the distinction is
def cmp_teams(t1,t2):
	# Head to head
	t1_won = False
	t2_won = False
	for game in teams[t1]:
		if (game[1] == t2):
			if game[0] == "W":
				t1_won = True
			else:
				t2_won = True
	if t1_won and not t2_won:
		return (True,30)
	elif t2_won and not t1_won:
		return (False,30)
	else:
		pass

	# Record against common opponents
	team1_opps = [game[1] for game in teams[t1]]
	team2_opps = [game[1] for game in teams[t2]]
	common_opps = [team for team in team1_opps if team in team2_opps]

	team1_common_opp_wins,_,t1_homecount,_ = record_vs_opp_set(t1,common_opps)
	team2_common_opp_wins,_,t2_homecount,_ = record_vs_opp_set(t2,common_opps)
	if team1_common_opp_wins > team2_common_opp_wins:
		return (True,10+2*len(common_opps))
	elif team2_common_opp_wins > team1_common_opp_wins:
		return (False,10+2*len(common_opps))
	else:
		pass # eliminating home/away tiebreak for now.  Maybe later we can insert it as a lower priority decision	
	# Some setup for the rest
	(t1_wins,t1_losses,t1_h,t1_a) = record_vs_opp_set(t1,team1_opps)
	(t2_wins,t2_losses,t2_h,t2_a) = record_vs_opp_set(t2,team2_opps)

	# Short-circuit if one team has won four fewer games.  This is to get
	# rid of FCS teams who only play an FBS team once or twice and win them all
	if t1_wins > t2_wins + 3:
		return (True,9)
	elif t2_wins > t1_wins + 3:
		return (False,9)

	# AAMOV against common opponents
	aamco1 = avg_adjusted_mov_oppset(t1, common_opps)
	aamco2 = avg_adjusted_mov_oppset(t2, common_opps)

	if abs(aamco1 - aamco2) >= 21:
		return ((aamco1 > aamco2), 7)
	elif abs(aamco1 - aamco2) >= 14:
		return ((aamco1 > aamco2), 6)
	elif abs(aamco1 - aamco2) >= 7:
		return ((aamco1 > aamco2), 5)
	# If the aamcos are within 7, it's too close, lets move on to other factors

	# Best wins weighted by aamov
	wabw1 = weighted_average_best_wins(t1)
	wabw2 = weighted_average_best_wins(t2)
	aam1 = avg_adjusted_mov(t1)
	aam2 = avg_adjusted_mov(t2)

	# aams are on a -21 to 21 scale.  Normalize
	naam1 = (aam1 + 21)/42
	naam2 = (aam2 + 21)/42

	wwabw1 = (wabw1 * naam1*mov_weight) + (wabw1 * wins_weight)
	wwabw2 = (wabw2 * naam2*mov_weight) + (wabw2 * wins_weight)

	if wwabw1 > wwabw2:
		return (True, 4)
	elif wwabw2 > wwabw1:
		return (False, 4)
	else:
		# I guess it could happen in week 1?
		pass

	# Who has the best wins?
	wabw1 = weighted_average_best_wins(t1)
	wabw2 = weighted_average_best_wins(t2)

	if wabw1 > wabw2:
		return (True,3)
	elif wabw2 > wabw1:
		return (False,3)
	else:
		pass
	
	# Overall record
	t1_percent = t1_wins/(t1_wins+t1_losses)
	t2_percent = t2_wins/(t2_wins+t2_losses)
	if t1_percent > t2_percent:
		return (True,2)
	elif t2_percent > t1_percent:
		return (False,2)
	else:
		# tiebreak on home vs away
		if t1_a > t2_a:
			return (True,1.5)
		elif t2_a > t1_a:
			return (False,1.5)
		else:
			pass

	# average adjusted margin of victory
	aam1 = avg_adjusted_mov(t1)
	aam2 = avg_adjusted_mov(t2)
	if aam1 > aam2:
		return (True,1)
	elif aam2 > aam1:
		return (False,1)
	else:
		pass

	# More wins are better
	if t1_wins > t2_wins:
		return (True,0.5)
	elif t2_wins > t1_wins:
		return (False,0.5)
	else:
		pass

	# I give up, these teams are identical
	return (None,0)

# For a set of opponents, what is a teams record against them
def record_vs_opp_set(team,opps):
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
	return (wins,losses,home_count,away_count)

# Calculates the weighted average of the number of wins of the three highest win total win of 
# a given team.  Uses the formula: (3*best_win + 2*second_best_win + third_best_win)/6
def weighted_average_best_wins(team):
	if "team_wins" not in weighted_average_best_wins.__dict__:
		weighted_average_best_wins.team_wins = {}

	opp_wins = []

	if current_week < 5:
		# Modify the wins by the win totals last year
		mod_weight = (float(5-current_week))/4 # week 1 - 100%, week 2 - 75%, week 3 - 50%, week 4: 25%
	
	for game in teams[team]:
		if game[0] == "W":
			if not game[1] in weighted_average_best_wins.team_wins.keys():
				w,l,_,_ = record_vs_opp_set(game[1],teams)
				weighted_average_best_wins.team_wins[game[1]] = float(w)/(float(w)+float(l))
				if current_week < 5:
					if game[1] in prev_year_recs.keys():
						weighted_average_best_wins.team_wins[game[1]] = weighted_average_best_wins.team_wins[game[1]] * (1.0 - mod_weight) \
												+ prev_year_recs[game[1]] * mod_weight
					else:
						# If the opponent isn't in the prev_year_recs hash table, they didn't play any games last year
						weighted_average_best_wins.team_wins[game[1]] = weighted_average_best_wins.team_wins[game[1]] * (1.0 - mod_weight)
				opp_wins.append(w)
			else:
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

# Calculates the average margin of victory over all games, but setting all totals above 21 to 21
# because there really isn't much of a difference after a 3 TD lead and we don't want to reward
# running up the score
def avg_adjusted_mov(team):
	num_games = 0.0
	total_margin = 0.0
	for game in teams[team]:
		margin = game[2]-game[3]
		if abs(margin) > max_mov:
			if margin > 0:
				margin = max_mov
			else:
				margin = -max_mov
		num_games += 1
		total_margin += margin
	return total_margin / num_games

def avg_adjusted_mov_oppset(team, opps):
	num_games = 0.0
	total_margin = 0.0
	for game in teams[team]:
		if game[1] in opps:
			margin = game[2]-game[3]
			if abs(margin) > max_mov:
				if margin > 0:
					margin = max_mov
				else:
					margin = -max_mov
			num_games += 1
			total_margin += margin
	if num_games > 0:
		return total_margin / num_games
	else:
		# All teams call into this function regardless of whether they have common games
		# Returning 0 means that they have the same AAM against their empty set of common opponents
		return 0


# What is the quality of a given team ordering?  Lower is better
def order_quality(teams_arr):
	quality = 0
	i = 0
	j = 1
	for team1 in teams_arr:
		for team2 in teams_arr[i:]:
			diff,weight = teamcmps[(team2,team1)]
			if diff:
				quality += weight*(j-i)
			j += 1
		i+=1
		j=i+1
	return quality
		
# Iteratively order the teams given an initial order.  Python doesn't optimize tail recursion
# which makes me extremely unhappy
def order_teams(team_order):
	misses = 0
	num_teams = len(team_order)
	num_misses_to_continue = (num_teams/2) * (num_teams + 1) # == 1+...+num_teams
	k = 0
	initial_quality = order_quality(team_order)
	switch_cache = Set()
	while (k < max_iterations) and (misses < num_misses_to_continue):
		condition = True
		while condition:
			i = random.randint(0,num_teams-1)
			j = random.randint(0,num_teams-1)
			condition = (i,j) in switch_cache
		switch_cache.add((i,j))
		switch_cache.add((j,i))
		team_order[i],team_order[j] = team_order[j],team_order[i]
		new_quality = order_quality(team_order)
		if (new_quality >= initial_quality):
			# Didn't help :(
			team_order[i],team_order[j] = team_order[j],team_order[i]
			misses += 1
		else:
			# Only overwrite if we changed something
			initial_quality = new_quality
			misses = 1 # We won't be retrying the previous ordering, so count that as a miss
			k+=1
			switch_cache.clear()
			# Don't retry the ordering we just did
			switch_cache.add((i,j))
			switch_cache.add((j,i))
	print "Ordered teams:\n\tMisses: %d\n\tIterations: %d\n\tQuality: %d"%(misses,k,initial_quality)
	return team_order

# Loads a hash table with last years team names and win counts
def load_prev_year_records():
	f = open(prev_year_data_file, "rb")
	reader = csv.reader(f)
	res = {}
	rownum = 0
	for row in reader:
		if rownum == 0:
			next
		else:	
			if (row[tsh_col] == ' ' or row[tsh_col] == '' or row[tsv_col] == ' ' or row[tsv_col] == ''):
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

random.seed()

f = open(infile, "rb")
reader = csv.reader(f)

teams = {}

rownum = 0
for row in reader:
	if rownum == 0:
		next
	else:
		if (row[tsh_col] == ' ' or row[tsh_col] == '' or row[tsv_col] == ' ' or row[tsv_col] == ''):
			continue
		visitorname = row[tnv_col]
		homename = row[tnh_col]
		visitorscore = int(row[tsv_col])
		homescore = int(row[tsh_col])

		if (not visitorname in teams.keys()):
			teams[visitorname] = []
		if (not homename in teams.keys()):
			teams[homename] = []
		

		teams[visitorname].append(["W" if (visitorscore > homescore) else "L"
				       ,homename,visitorscore,homescore,"A"])
		teams[homename].append(["W" if (homescore > visitorscore) else "L"
				    ,visitorname,homescore,visitorscore,"H"])
		
	rownum += 1 

if current_week < 5:
	# prev_year_recs is a hash table where the keys are team names and the values are the number of wins they had last year
	prev_year_recs = load_prev_year_records()

# Compare all teams
teamcmps = {}

metric_counts = {}
total_cmps = 0

for team1 in teams.keys():
	for team2 in teams.keys():
		teamcmps[(team1,team2)] = cmp_teams(team1,team2)
		teamcmps[(team2,team1)] = cmp_teams(team2,team1)
		# Count up how frequently each metric is used to determine the comparison
		weight = teamcmps[(team1,team2)][1]
		# Collapse "Common opps" to one point
		if (weight < 30 and weight >= 10):
			weight = 10
		if weight in metric_counts:
			metric_counts[weight] += 1
		else:
			metric_counts[weight] = 1
		total_cmps += 1

big_ten = ["Northwestern","Wisconsin", "Michigan", "Indiana", "Purdue", "Illinois", "Maryland", "Rutgers", "Ohio State", "Minnesota", "Nebraska", "Michigan State", "Penn State", "Iowa"] 

if len(sys.argv) == 1: 
	# Print out a ranking
	team_order = order_teams(teams.keys())

	num = 0
	for team in team_order:
		num += 1
		if num > 30 and team not in big_ten:
			continue
		wins,losses,_,_ = record_vs_opp_set(team, [game[1] for game in teams[team]])
		print "%d. %s (%d-%d)"%(num,team, wins,losses)

	# Print out the metrics used:
	print "\nMetrics:"
	for (metric, m_count) in metric_counts.iteritems():
		print "%s: %0.2f%%"%(human_readable_cmps(metric),100*float(m_count)/float(total_cmps)) 

elif len(sys.argv) == 2:
	# Display info about the team
	for game in teams[sys.argv[1]]:
		w,l,_,_ = record_vs_opp_set(game[1],teams)
		print "%s - %s: %d-%d"%(game[0],game[1],w,l)
	print "AAMOV: %f"%avg_adjusted_mov(sys.argv[1])
	print "WABW: %f"%weighted_average_best_wins(sys.argv[1])

elif len(sys.argv) == 3:
	# Print the relative ranking between the teams and its weight (which gives you the reason)
	# If "all" is the second argument, display the first team vs all teams
	if sys.argv[2] == "all":
		for team in teams.keys():
			(val,weight) = teamcmps[(sys.argv[1],team)]
			print "%s - %s: %s"%(team,val,human_readable_cmps(weight))
			
	else:
		(val, weight) = teamcmps[(sys.argv[1],sys.argv[2])]
		print (val,human_readable_cmps(weight))
else:
	# Print the quality of the given ordering
	for team in sys.argv[1:]:
		if team not in teams.keys():
			print "%s not found"%team
	print order_quality(sys.argv[1:])
