#!/usr/bin/python

import unittest
import constants

from ranker import cmp_teams
from ranker import record_vs_opp_set
from ranker import calculate_wabw_team_wins
from ranker import weighted_average_best_wins
from ranker import avg_adjusted_mov
from ranker import avg_adjusted_mov_oppset
from ranker import order_quality
from ranker import order_teams

class RankerTestCases(unittest.TestCase):
	teams1 = { "AAAA" : [["W","BBBB",10,0,"H"],
			     ["W","CCCC",10,0,"A"]],
		   "BBBB" : [["L","AAAA",0,10,"A"],
			     ["W","CCCC",10,0,"H"]],
		   "CCCC" : [["L","AAAA",0,10,"H"],
			     ["L","BBBB",0,10,"A"]] }

	teams2 = { "DDDD" : [["W","EEEE",10,0,"A"]],
		   "FFFF" : [["L","EEEE",0,10,"H"],
			     ["W","GGGG",10,0,"H"]],
		   "HHHH" : [["W","EEEE",20,0,"H"],
			     ["W","GGGG",10,0,"A"]],
		   "IIII" : [["W","GGGG",40,0,"A"]],
		   "JJJJ" : [["W","EEEE",1,0,"A"],
			     ["W","GGGG",1,0,"H"]],
		   "KKKK" : [["L","EEEE",0,30,"A"],
			     ["W","GGGG",21,20,"H"],
			     ["W","HHHH",21,19,"A"],
			     ["L","IIII",0,30,"A"]],
		   "LLLL" : [["L","EEEE",0,3,"H"],
			     ["W","GGGG",40,0,"A"],
			     ["W","HHHH",40,0,"H"],
			     ["L","IIII",0,3,"H"]],
		   "MMMM" : [["W","EEEE",40,0,"H"],
			     ["L","GGGG",0,1,"A"]] }

	teams3 = { "NNNN" : [["W", "OOOO", 10, 0, "A"],
			     ["L", "PPPP", 0, 10, "H"],
			     ["L", "QQQQ", 0, 20, "A"],
			     ["L", "RRRR", 0, 30, "H"]],
		   "OOOO" : [["L", "NNNN", 0, 10, "H"],
			     ["W", "PPPP", 15, 0, "H"],
			     ["W", "QQQQ", 15, 0, "A"],
			     ["L", "RRRR", 0, 20, "A"]],
		   "PPPP" : [["W", "NNNN", 10, 0, "A"],
			     ["L", "OOOO", 0, 15, "A"],
			     ["W", "QQQQ", 15, 9, "H"],
			     ["W", "RRRR", 10, 9, "H"]],
		   "QQQQ" : [["W", "NNNN", 20, 0, "H"],
			     ["L", "OOOO", 0, 15, "H"],
			     ["L", "PPPP", 9, 15, "A"],
			     ["L", "RRRR", 0, 30, "A"]],
		   "RRRR" : [["W", "NNNN", 30, 0, "A"],
			     ["W", "OOOO", 20, 0, "H"],
			     ["L", "PPPP", 9, 10, "A"],
			     ["W", "QQQQ", 0, 30, "H"]] }

	def test_cmp_teams_head_to_head_works(self):
		self.assertTrue((True, constants.hth_cmp_weight) == cmp_teams(self.teams1,{},"AAAA","BBBB"))
		self.assertTrue((False, constants.hth_cmp_weight) == cmp_teams(self.teams1,{},"BBBB","AAAA"))


	def test_cmp_teams_common_opps_record_works(self):
		self.assertTrue((True, constants.co_base_cmp_weight + 2) == cmp_teams(self.teams2,{},"DDDD","FFFF"))
		self.assertTrue((False, constants.co_base_cmp_weight + 2) == cmp_teams(self.teams2,{},"FFFF","DDDD"))
		self.assertTrue((False, constants.co_base_cmp_weight + 4) == cmp_teams(self.teams2,{},"FFFF","HHHH"))
		self.assertTrue((True, constants.co_base_cmp_weight + 4) == cmp_teams(self.teams2,{},"HHHH","FFFF"))


	def test_cmp_teams_aamov_co_works(self):
		self.assertTrue((True, constants.aamco_7_cmp_weight) == cmp_teams(self.teams2,{},"HHHH","DDDD"))
		self.assertTrue((True, constants.aamco_7_cmp_weight) == cmp_teams(self.teams2,{},"IIII","HHHH"))
		self.assertTrue((True, constants.aamco_14_cmp_weight) == cmp_teams(self.teams2,{},"HHHH","JJJJ"))
		self.assertTrue((True, constants.aamco_14_cmp_weight) == cmp_teams(self.teams2,{},"LLLL","KKKK"))
		self.assertTrue((True, constants.aamco_14_cmp_weight) == cmp_teams(self.teams2,{},"MMMM","KKKK"))


	def test_cmp_teams_wwabw_works(self):
		pass  # TODO

	def test_record_vs_opp_set_works(self):
		self.assertTrue((2,0,1,1) == record_vs_opp_set(self.teams1,"AAAA",["BBBB","CCCC"]))
		self.assertTrue((1,0,1,0) == record_vs_opp_set(self.teams1,"AAAA",["BBBB"]))
		self.assertTrue((1,1,1,1) == record_vs_opp_set(self.teams1,"BBBB",["AAAA","CCCC"]))
		self.assertTrue((0,2,1,1) == record_vs_opp_set(self.teams1,"CCCC",["AAAA","BBBB"]))
		self.assertTrue((0,0,0,0) == record_vs_opp_set(self.teams1,"CCCC",["XXXX","YYYY","ZZZZ"]))


	def test_calculate_wabw_team_wins_works(self):
		saved_current_week = constants.current_week
		prev_year_recs = {}  # TODO: Test with previous year records

		constants.current_week = 5
		self.assertTrue(1 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "NNNN", self.teams3.keys(), 0))
		self.assertTrue(2 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "OOOO", self.teams3.keys(), 0))
		self.assertTrue(3 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "PPPP", self.teams3.keys(), 0))
		self.assertTrue(1 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "QQQQ", self.teams3.keys(), 0))
		self.assertTrue(3 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "RRRR", self.teams3.keys(), 0))

		constants.current_week = 3
		self.assertTrue(0.5 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "NNNN", self.teams3.keys(), .5))
		self.assertTrue(1   == calculate_wabw_team_wins(self.teams3, prev_year_recs, "OOOO", self.teams3.keys(), .5))
		self.assertTrue(1.5 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "PPPP", self.teams3.keys(), .5))
		self.assertTrue(0.5 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "QQQQ", self.teams3.keys(), .5))
		self.assertTrue(1.5 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "RRRR", self.teams3.keys(), .5))

		constants.current_week = 1
		self.assertTrue(0 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "NNNN", self.teams3.keys(), 1))
		self.assertTrue(0 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "OOOO", self.teams3.keys(), 1))
		self.assertTrue(0 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "PPPP", self.teams3.keys(), 1))
		self.assertTrue(0 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "QQQQ", self.teams3.keys(), 1))
		self.assertTrue(0 == calculate_wabw_team_wins(self.teams3, prev_year_recs, "RRRR", self.teams3.keys(), 1))


		constants.current_week = saved_current_week


	def test_weighted_average_best_wins_works(self):
		saved_current_week = constants.current_week
		prev_year_recs = {}  # TODO: Test with previous year records

		constants.current_week = 5
		self.assertTrue(2.0 == weighted_average_best_wins(self.teams3, prev_year_recs, "NNNN"))
		self.assertTrue(2.2 == weighted_average_best_wins(self.teams3, prev_year_recs,  "OOOO"))
		self.assertTrue(2   == weighted_average_best_wins(self.teams3, prev_year_recs, "PPPP"))
		self.assertTrue(1.0 == weighted_average_best_wins(self.teams3, prev_year_recs, "QQQQ"))
		self.assertTrue(1.5 == weighted_average_best_wins(self.teams3, prev_year_recs, "RRRR"))

		constants.current_week = 3
		weighted_average_best_wins.team_wins = {}
		self.assertTrue(1.0  == weighted_average_best_wins(self.teams3, prev_year_recs, "NNNN"))
		self.assertTrue(1.1  == weighted_average_best_wins(self.teams3, prev_year_recs, "OOOO"))
		self.assertTrue(1    == weighted_average_best_wins(self.teams3, prev_year_recs, "PPPP"))
		self.assertTrue(0.5  == weighted_average_best_wins(self.teams3, prev_year_recs, "QQQQ"))
		self.assertTrue(0.75 == weighted_average_best_wins(self.teams3, prev_year_recs, "RRRR"))


		constants.current_week = 1
		weighted_average_best_wins.team_wins = {}
		self.assertTrue(0 == weighted_average_best_wins(self.teams3, prev_year_recs, "NNNN"))
		self.assertTrue(0 == weighted_average_best_wins(self.teams3, prev_year_recs, "OOOO"))
		self.assertTrue(0 == weighted_average_best_wins(self.teams3, prev_year_recs, "PPPP"))
		self.assertTrue(0 == weighted_average_best_wins(self.teams3, prev_year_recs, "QQQQ"))
		self.assertTrue(0 == weighted_average_best_wins(self.teams3, prev_year_recs, "RRRR"))


		constants.current_week = saved_current_week


	def test_avg_adjusted_mov_works(self):
		self.assertTrue(10 == avg_adjusted_mov(self.teams2, "DDDD"))
		self.assertTrue(0 == avg_adjusted_mov(self.teams2, "FFFF"))
		self.assertTrue(15 == avg_adjusted_mov(self.teams2, "HHHH"))
		self.assertTrue(21 == avg_adjusted_mov(self.teams2, "IIII"))
		self.assertTrue(-9.75 == avg_adjusted_mov(self.teams2, "KKKK"))
		self.assertTrue(9 == avg_adjusted_mov(self.teams2, "LLLL"))



	def test_avg_adjusted_mov_oppset(self):
		self.assertTrue(10 == avg_adjusted_mov_oppset(self.teams2, "DDDD", ["EEEE"]))
		self.assertTrue(-10 == avg_adjusted_mov_oppset(self.teams2, "FFFF", ["EEEE"]))
		self.assertTrue(0 == avg_adjusted_mov_oppset(self.teams2, "FFFF", ["EEEE", "GGGG"]))
		self.assertTrue(15 == avg_adjusted_mov_oppset(self.teams2, "HHHH", ["EEEE", "GGGG"]))
		self.assertTrue(21 == avg_adjusted_mov_oppset(self.teams2, "IIII", ["GGGG"]))
		self.assertTrue(21 == avg_adjusted_mov_oppset(self.teams2, "IIII", ["GGGG", "NOTANOPPONENT"]))
		self.assertTrue(-10 == avg_adjusted_mov_oppset(self.teams2, "KKKK", ["EEEE", "GGGG"]))
		self.assertTrue(-6 == avg_adjusted_mov_oppset(self.teams2, "KKKK", ["EEEE", "GGGG", "HHHH"]))
		self.assertTrue(-9.75 == avg_adjusted_mov_oppset(self.teams2, "KKKK", ["EEEE", "GGGG", "HHHH", "IIII"]))
		self.assertTrue(9 == avg_adjusted_mov_oppset(self.teams2, "LLLL", ["EEEE", "GGGG"]))
		self.assertTrue(13 == avg_adjusted_mov_oppset(self.teams2, "LLLL", ["EEEE", "GGGG", "HHHH"]))
		self.assertTrue(9 == avg_adjusted_mov_oppset(self.teams2, "LLLL", ["EEEE", "GGGG", "HHHH", "IIII"]))


	def test_order_quality_works(self):
		teamcmps = {}
		teamcmps[("A","B")] = (True, 30)
		teamcmps[("B","A")] = (False, 30)
		teamcmps[("A","A")] = (None, 0)
		teamcmps[("B","B")] = (None, 0)

		# Lower order quality is a better ranking
		self.assertTrue(order_quality(["A", "B"],teamcmps) < order_quality(["B", "A"], teamcmps))

		teamcmps[("A","C")] = (True, 12)
		teamcmps[("C","A")] = (False, 12)
		teamcmps[("B","C")] = (True, 30)
		teamcmps[("C","B")] = (False, 30)
		teamcmps[("C","C")] = (None, 0)

		self.assertTrue(order_quality(["A", "B", "C"],teamcmps) < order_quality(["B", "A", "C"], teamcmps))
		self.assertTrue(order_quality(["C", "A", "B"],teamcmps) < order_quality(["C", "B", "A"], teamcmps))
		self.assertTrue(order_quality(["A", "C", "B"],teamcmps) < order_quality(["C", "A", "B"], teamcmps))
		self.assertTrue(order_quality(["B", "A", "C"],teamcmps) < order_quality(["B", "C", "A"], teamcmps))

	def team_order_teams_works(self):
		for t1 in teams1.keys():
			for t2 in teams1.keys():
				teamcmps[(t1,t2)] = cmp_teams(teams1, {}, t1, t2)
				teamcmps[(t2,t1)] = cmp_teams(teams1, {}, t2, t1)

		assertTrue(["AAAA","BBBB","CCCC"] == order_teams(teams1.keys()))

if __name__ == '__main__':
	unittest.main()
