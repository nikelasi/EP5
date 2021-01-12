
def get_interest_cost(current_interest):
	#formula: 70,000(interest)^(interest*0.35)
	cost = int(round(70_000*current_interest**(current_interest*0.35), -3))
	return cost

def get_prestige_cost(current_prestige):
	#formula: 100,000(1.25(rank+1))
	cost = int(round(100_000 * ((current_prestige+1)*1.25)))
	return cost