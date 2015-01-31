#!/usr/bin/python

import unittest

from ranker import cmp_teams
from ranker import record_vs_opp_set


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
			     ["W","GGGG",10,0,"A"]] }

	def test_cmp_teams_head_to_head_works(self):
		self.assertTrue((True,30) == cmp_teams(self.teams1,"AAAA","BBBB"))
		self.assertTrue((False,30) == cmp_teams(self.teams1,"BBBB","AAAA"))

	def test_cmp_teams_common_opps_record_works(self):
		self.assertTrue((True,12) == cmp_teams(self.teams2,"DDDD","FFFF"))
		self.assertTrue((False,12) == cmp_teams(self.teams2,"FFFF","DDDD"))
		self.assertTrue((False,14) == cmp_teams(self.teams2,"FFFF","HHHH"))
		self.assertTrue((True,14) == cmp_teams(self.teams2,"HHHH","FFFF"))

	def test_cmp_teams_aamov_co_works(self):
		self.assertTrue((True,5) == cmp_teams(self.teams2,"HHHH","DDDD"))


	def test_record_vs_opp_set_works(self):
		self.assertTrue((2,0,1,1) == record_vs_opp_set(self.teams1,"AAAA",["BBBB","CCCC"]))
		self.assertTrue((1,0,1,0) == record_vs_opp_set(self.teams1,"AAAA",["BBBB"]))
		self.assertTrue((1,1,1,1) == record_vs_opp_set(self.teams1,"BBBB",["AAAA","CCCC"]))
		self.assertTrue((0,2,1,1) == record_vs_opp_set(self.teams1,"CCCC",["AAAA","BBBB"]))
		self.assertTrue((0,0,0,0) == record_vs_opp_set(self.teams1,"CCCC",["XXXX","YYYY","ZZZZ"]))


if __name__ == '__main__':
	unittest.main()
