import sys
import redis

def find(redis, key_namespace, predicate, action):
	keys = redis.keys(key_namespace + "*")
	for key in keys:
		value = redis.get(key)
		if predicate(key, value):
			action(key, value)

def parse_host_spec(spec):
	host_password = spec.split('@')
	if len(host_password) > 1:
		password = host_password[0]
		host = host_password[1]
	else:
		password = ''
		host = host_password[0]
	return [host, password]

def main():
	if sys.argv[1] == "--help":
		print_help()
		return

	if len(sys.argv) < 4:
		print_help()
		return

	try:
		host, password = parse_host_spec(sys.argv[1])		
	except:
		print "Invalid host specification"
		print_help()
		return

	r = redis.Redis(host=host, password=password)

	key_namespace = ''
	value_to_find = ''
	if len(sys.argv) > 2:
		key_namespace = sys.argv[2]

	if len(sys.argv) > 3:
		value_to_find = sys.argv[3]

	matching_keys = []
	find(r, key_namespace, lambda key, value: value == value_to_find, lambda key, value: matching_keys.append(key))
	if len(matching_keys) == 0:
		print "No matches found"
	else:
		sorted_matches = sorted(matching_keys)
		for match in sorted_matches:
			print match

def print_help():
	print "Usage: python redis-find.py [<password>@]<host> <key namespace/prefix> <value to find>"
	print "[Note: An empty namespace ('') will search through all keys]"

if __name__ == '__main__':
    main()
