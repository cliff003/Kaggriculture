import sys, time
from kaggle_environments import make
path = sys.argv[1]
t = time.time()
env = make("kaggriculture", debug=False)
env.run([path, path])
last = env.steps[-1]
print("status", [s.status for s in last], "reward", [s.reward for s in last], "steps", len(env.steps), "wall", round(time.time() - t, 1))
