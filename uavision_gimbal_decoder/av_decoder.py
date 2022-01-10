# module to connect to a MPEG-TS stream and decode KLV packets from a KLV stream
import av
from .packet_decoder import decodePacket


def decode_from_ts_stream(stream_path: str) -> None:
    with av.open(stream_path) as input_:
        # Make an output stream using the input as a template. This copies the stream
        # setup from one to the other.
        in_data = input_.streams.data[0]

        for packet in input_.demux(in_data):
            # We need to skip the "flushing" packets that `demux` generates.
            if packet.dts is None:
                continue

            decoded_packet = decodePacket(packet.to_bytes())
            yield decoded_packet
