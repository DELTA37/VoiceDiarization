from speakerDiarization import SpeakerDiarization
from flasklib.creator import Creator
from flasklib.audio_field import AudioField
from flasklib.output_audio_field import OutputAudioField
from flasklib.output_diarization_field import OutputDiarizationField
import soundfile as sf
from io import BytesIO
import numpy as np
import argparse


def algo_fn(audio):
    spk = SpeakerDiarization()
    buf = BytesIO()
    sf.write(buf, audio[0], audio[1], format='wav', closefd=False)
    buf.seek(0)
    output = spk.predict(buf)
    return {
        'output_audio': audio,
        'output_diar': output,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=8000, type=int)
    args = parser.parse_args()
    creator = Creator("Example", algo_fn, [
        AudioField("audio"),
    ], [
        OutputAudioField("output_audio", np.random.randn(*(100, 2))),
        OutputDiarizationField("output_diar", {}),
    ])
    creator.start_server(host=args.host, port=args.port)
