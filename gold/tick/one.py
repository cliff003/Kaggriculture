import sys, json
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import gstat
if __name__ == '__main__':
    a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    r = gstat.play_one((a, b, seed, 0))
    print('rewards', r['rewards'], 'status', r['status'], 'errors', r['errors'], 'ms', r['time_ms'])
    import fastarena
