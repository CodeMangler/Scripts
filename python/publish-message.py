import sys
import kombu
import kombu.connection

def main():
	if len(sys.argv) < 4:
		print_help()
		return

	address = sys.argv[1]
	exchange_name = sys.argv[2]
	message = sys.argv[3]

	connection = kombu.BrokerConnection(address)
	exchange = kombu.Exchange(exchange_name)
	channel = connection.channel()
	producer = kombu.Producer(channel, exchange=exchange, serializer="json")
	producer.publish(message)

	producer.close()
	connection.close()

def print_help():
	print "Usage: python publish-message.py <hostname/url> <exchange name> <json_message>"
	print "Example: python publish-message.py localhost an_exchange '{\"foo\": \"bar\"}'"
	print "OR: python publish-message.py amqp://guest:guest@localhost:5672/ an_exchange '{\"foo\": \"bar\"}'"

if __name__ == '__main__':
    main()
