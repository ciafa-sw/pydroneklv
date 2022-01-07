# create a klv data stream with UDP connection with the following command
# ffmpeg -re -i backup.ts -map 0:1 -c copy -f mpegts udp://localhost:20000

import av
import argparse
from uavision_gimbal_decoder.packet_decoder import decodePacket

parser = argparse.ArgumentParser(description='Parse KLV packets from a data stream in a MPEG-TS UDP connection.')
parser.add_argument('address', type=str,
                    help='address of UDP connection')
parser.add_argument('port', type=int,
                    help='port of UDP connection')

args = parser.parse_args()
print(args)

input_ = av.open(f"udp://{args.address}:{args.port}")

# Make an output stream using the input as a template. This copies the stream
# setup from one to the other.
in_data = input_.streams.data[0]

for packet in input_.demux(in_data):
    # We need to skip the "flushing" packets that `demux` generates.
    if packet.dts is None:
        continue

    decodedPacket = decodePacket(packet.to_bytes())
    print(decodedPacket)

input_.close()