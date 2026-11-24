# Domain beats horizon: a personal task with a near deadline goes to ## Personal, not ## Now.
from evalkit import *
t = read("tasks.md")
expect(any("valuation" in l.lower() for l in task_lines(t, "Personal")), "task is not in ## Personal")
expect(not any("valuation" in l.lower() for l in task_lines(t, "Now")), "personal task was filed in ## Now")
expect(len(task_lines(t, "Now")) <= 7, "## Now is over the cap of 7")
done()
