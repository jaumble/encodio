import math
import wave
import struct
import numpy as np
import pyaudio

char_freq = [
    ("a", 261.626), # C4
    ("b", 277.183),
    ("c", 293.665),
    ("d", 311.127),
    ("e", 329.628),
    ("f", 349.228),
    ("g", 369.994),
    ("h", 391.995),
    ("i", 415.305),
    ("j", 440.000),
    ("k", 466.164),
    ("l", 493.885),
    ("m", 523.251), # C5
    ("n", 554.365),
    ("o", 587.330),
    ("p", 622.254),
    ("q", 659.255),
    ("r", 698.456),
    ("s", 739.989),
    ("t", 783.991),
    ("u", 830.609),
    ("v", 880.000),
    ("w", 932.328),
    ("x", 987.767),
    ("y", 1046.50), # C6
    ("z", 1108.73),
    (" ", 1174.66)
] #TODO: use an equation for this, map to ascii

char_to_freq = {char:freq for char, freq in char_freq}
freq_to_char = {freq:char for char, freq in char_freq}

def message_to_audio(filename, char_len, message, amplitude=8000.0):
    """
    Takes a message and generates an audio file from it, given the specified character length in frames.
    For best results, use 50 or more frames.
    """
    frate = 10000.0 # framerate as a float
    note_length = char_len
    num_tones = len(message)
    data_size = num_tones * int(frate)
    fname = filename

    wav_file = wave.open(fname, "w")

    nchannels = 1
    sampwidth = 2
    framerate = int(frate)
    nframes = data_size
    comptype = "NONE"
    compname = "not compressed"

    wav_file.setparams((nchannels, sampwidth, framerate, nframes,
        comptype, compname))

    for char in message:
        freq = char_to_freq[char]
        sine_list_x = []

        for x in range(note_length):
            sine_list_x.append(math.sin(2*math.pi*freq*(x/frate)))

        for s in sine_list_x:
            wav_file.writeframes(struct.pack('h', int(s*amplitude/2)))

    wav_file.close()

def closest_char(freq):
    freqs = freq_to_char.keys()
    closest = min(freqs, key=lambda x:abs(x-freq))
    return freq_to_char[closest]

def audio_to_message(filename, char_len):
    """
    Takes an audio file and gets a message from it, given the stated character length in frames.
    Pitch detection stuff from https://github.com/pbouda/stuff/blob/master/soundexperiments/pitch_estimation.py.
    """
    chunk = char_len

    # open up a wave
    wf = wave.open(filename, 'rb')
    swidth = wf.getsampwidth()
    RATE = wf.getframerate()
    # use a Blackman window
    window = np.blackman(chunk)
    # open stream
    p = pyaudio.PyAudio()
    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = RATE,
                    output = True,
                    output_device_index = None)

    # read some data
    data = wf.readframes(chunk)
    message = ""
    # play stream and find the frequency of each chunk
    while len(data) == chunk*swidth:
        # write data out to the audio stream
        stream.write(data)
        # unpack the data and times by the hamming window
        indata = np.array(wave.struct.unpack("%dh"%(len(data)/swidth),\
                                            data))*window
        # Take the fft and square each value
        fftData=abs(np.fft.rfft(indata))**2
        # find the maximum
        which = fftData[1:].argmax() + 1
        # use quadratic interpolation around the max
        if which != len(fftData)-1:
            y0,y1,y2 = np.log(fftData[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            # find the frequency and output it
            thefreq = (which+x1)*RATE/chunk
        else:
            thefreq = which*RATE/chunk
        message += closest_char(thefreq)
        # read some more data
        data = wf.readframes(chunk)
    if data:
        stream.write(data)
    stream.close()
    p.terminate()
    return message



filename = "not_a_story_the_jedi_would_tell_you.wav"
plagueis = "did you ever hear the tragedy of darth plagueis the wise"
char_len = 1000
message_to_audio(filename, char_len, plagueis)
print(audio_to_message(filename, char_len))