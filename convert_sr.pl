#!/usr/bin/perl

print "Date,Visitor,Visitor Score,Home Team,Home Score,Line\n";

while(<>) {
	if(/^Rk/) {
		next;
	}
	if(/^\d+,\d+,(\w+\s\d\d?\s\d\d\d\d),\d\d?:\d\d \w\w,\w+,(\(\d\d?\)\s)?(.*?),(\d*)?,(@?),(\(\d\d?\)\s)?(.*?),(\d*)?,.*,.*$/) { 
		if ($5 eq "@"){
			print "$1,$3,$4,$7,$8,\n";
		} else {
			print "$1,$7,$8,$3,$4,\n";
		}
	}
}
