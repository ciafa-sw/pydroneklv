# create a klv data stream with UDP connection with the following command
# ffmpeg -re -i backup.ts -map 0:1 -c copy -f mpegts udp://localhost:20000

import argparse
from uavision_gimbal_decoder.av_decoder import decode_from_ts_stream

parser = argparse.ArgumentParser(description='Parse KLV packets from a data stream in a MPEG-TS UDP connection.')
parser.add_argument('address', type=str,
                    help='address of UDP connection')
parser.add_argument('port', type=int,
                    help='port of UDP connection')

args = parser.parse_args()

for p in (decode_from_ts_stream(f"udp://{args.address}:{args.port}")):
    print('\n'*4)
    print(p)
