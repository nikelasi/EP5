
def seconds_to_time(seconds):

	days = (seconds // (60*60*24)), "day"
	seconds %= (60*60*24)

	hours = (seconds // (60*60)), "hour"
	seconds %= (60*60)

	minutes = (seconds // (60)), "minute"
	seconds = seconds % 60, "second"

	_time = []
	for u, m in [days, hours, minutes, seconds]:
		if u:
			if u > 1:
				m += "s"
			_time.append(f"{u} {m}")

	return ", ".join(_time)
