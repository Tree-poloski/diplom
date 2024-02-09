import numpy as np
from skimage import io
from skimage.util import view_as_blocks
from scipy.fftpack import dct, idct
from matplotlib import pyplot as plt
%matplotlib inline

import warnings
warnings.filterwarnings('ignore')

u1, v1 = 4, 5
u2, v2 = 5, 4
n = 8

def double_to_byte(arr):
    return np.uint8(np.round(np.clip(arr, 0, 255), 0))

def increment_abs(x):
    return x + 1 if x >= 0 else x - 1

def decrement_abs(x):
    if np.abs(x) <= 1:
        return 0
    else:
        return x - 1 if x >= 0 else x + 1
    
def text_to_bin(text):
    a = [f'{i:b}' for i in text.encode('utf8')]
    a = ''.join(a)
    return np.array([i == '1' for i in a]).astype('int')

def to_string(bytes_):
    return ''.join([chr(int(b, 2)) for b in [bytes_[i*7: i*7 + 7] for i in range(len(bytes_) // 7)]])
def abs_diff_coefs(transform):
    return abs(transform[u1, v1]) - abs(transform[u2, v2])

def valid_coefficients(transform, bit, threshold):
    difference = abs_diff_coefs(transform)
    if (bit == 0) and (difference > threshold):
        return True
    elif (bit == 1) and (difference < -threshold):
        return True
    else:
        return False

def change_coefficients(transform, bit):
    coefs = transform.copy()
    if bit == 0:
        coefs[u1, v1] = increment_abs(coefs[u1, v1])
        coefs[u2, v2] = decrement_abs(coefs[u2, v2])
    elif bit == 1:
        coefs[u1, v1] = decrement_abs(coefs[u1, v1])
        coefs[u2, v2] = increment_abs(coefs[u2, v2])
    return coefs
def embed_bit(block, bit, P):
    patch = block.copy()
    coefs = dct(dct(patch, axis=0), axis=1)
    while not valid_coefficients(coefs, bit, P) or (bit != retrieve_bit(patch)):
        coefs = change_coefficients(coefs, bit)
        #print (coefs[u1, v1], coefs[u2, v2])
        patch = double_to_byte(idct(idct(coefs, axis=0), axis=1)/(2*n)**2)
    return patch

def embed_message(orig, msg, P):
    changed = orig.copy()
    blue = changed[:, :, 2]
    blocks = view_as_blocks(blue, block_shape=(n, n))
    h = blocks.shape[1]        
    for index, bit in enumerate(msg):
        #print ('index=%d, bit=%d' % (index, bit))
        i = index // h
        j = index % h
        block = blocks[i, j]
        blue[i*n: (i+1)*n, j*n: (j+1)*n] = embed_bit(block, bit, P)
    changed[:, :, 2] = blue
    return changed
def retrieve_bit(block):
    transform = dct(dct(block, axis=0), axis=1)
    return 0 if abs_diff_coefs(transform) > 0 else 1

def retrieve_message(img, length):
    blocks = view_as_blocks(img[:, :, 2], block_shape=(n, n))
    h = blocks.shape[1]
    return [retrieve_bit(blocks[index//h, index%h]) for index in range(length)]
text = '''
1 Introduction
The wide use of digitally formatted audio, video and printed information in network environment has
been slowed down by the lack of adequate protection on them. Developers and publishers hesitate to
distribute their sensitive or valuable materials because of the easiness of illicit copying and dissemination
[3],[6],[7].
Compared to ordinary paper form information, digitized multimedia information (image, text, audio,
video) provides many advantages, such as easy and inexpensive duplication and re-use, less expensive
and more flexible transmission either electronically (e.g. through the Internet) or physically (e.g. as
CD-ROM). Furthermore, transferring such information electronically through network is faster and
needs less efforts than physical paper copying, distribution and update. However, these advantages
also significantly increase the problems associated with enforcing copyright on the electronic information.
Basically, in order to protect distributed electronic multimedia information, we need two types of
protections. First, the multimedia data must contain a label or code, which identifies it uniquely as
property of the copyright holder. Second, the multimedia data should be marked in a manner which
allows its distribution to be tracked. This does not limit the number of copies allowed (vs. copy
protection), but provides a mean to check the original distributor. In order to prevent any copyright
forgery, misuse and violation, the copyright label must be unremovable and unalterable, and furthermore
survive processing which does not seriously reduce the quality of the data. This requires that first
the label must be secretly stored in a multimedia data, i.e. the locations for embedding this label are
secret, second the label must be robust even if the labeled multimedia data has been processed
incidentally or intentionally. '''

in_filename = '0-1.jpg'
out_filename = 'matlabik.jpg'
img_original = io.imread(in_filename)
test_message = text_to_bin(text)
img_changed = embed_message(img_original, test_message, 20)
io.imsave(out_filename, img_changed)