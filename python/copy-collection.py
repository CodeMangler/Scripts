import sys
import pymongo

def copy_collection(source_collection, destination_collection):
	source_entries = source_collection.find(timeout=False)
	count = 0
	try:
		for entry in source_entries:
			destination_collection.insert(entry)
			
			count += 1
			if count % 100 == 0:
				print "Copied " + str(count) + " documents"

		print "DONE - Copied " + str(count) + " documents"
	except Exception, e:
		raise e
	finally:
		del source_entries

def mongo_collection(collection_spec):
	host, port, username, password, db_name, collection_name = collection_spec
	connection = pymongo.Connection(host, port, safe=True)
	db = connection[db_name]
	db.authenticate(username, password)
	collection = db[collection_name]
	return [connection, db, collection]

def copy(source_spec, destination_spec):
	src_connection, src_db, src_collection = mongo_collection(source_spec)
	dst_connection, dst_db, dst_collection = mongo_collection(destination_spec)

	try:
		copy_collection(src_collection, dst_collection)
	except Exception, e:
		raise e
	finally:
		src_connection.disconnect()
		dst_connection.disconnect()

def parse_host_port(spec):
	host_port = spec.split(":")
	if len(host_port) > 1:
		host, port = host_port
	else:
		host = host_port[0]
		port = 27017
	return [host, port]

def parse_credentials(spec):
	user_password = spec.split(":")
	if len(user_password) > 1:
		username, password = user_password
	else:
		username = user_password[0]
		password = ""
	return [username, password]

def parse_host_spec(spec):
	host_credentials = spec.split("@")
	if len(host_credentials) > 1:
		username, password = parse_credentials(host_credentials[0])
		host, port = parse_host_port(host_credentials[1])
	else:
		username = password = ""
		host, port = parse_host_port(host_credentials[0])
	return [host, port, username, password]

def parse_connection_spec(spec):
	host_spec, db, collection = spec.split("/")
	host, port, username, password = parse_host_spec(host_spec)	
	return [host, port, username, password, db, collection]

def main():
	if len(sys.argv) < 3:
		print_help()
		return
	try:
		source_spec = parse_connection_spec(sys.argv[1])
	except Exception, e:
		print e
		print "Invalid source specification"
		print_help()
		return

	try:
		destination_spec = parse_connection_spec(sys.argv[2])
	except:
		print "Invalid destination specification"
		print_help()
		return

	copy(source_spec, destination_spec)

def print_help():
	print "Usage: python copy-collection.py <source> <destination>"
	print "<source> and <destination> should be specified in the format: [<username>:<password>@]<host>[:<port>]/<db>/<collection>"

if __name__ == '__main__':
    main()
