from pythonosc.udp_client import SimpleUDPClient


ip = "127.0.0.1"
port = 9000

client = SimpleUDPClient(ip, port)



client.send_message("/chatbox/input", ["test", True, False])