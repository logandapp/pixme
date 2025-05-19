from pixme.wrappers import change_lib_path
from pixme.extractors import *

if __name__ == '__main__':
    change_lib_path('../lib')

    extractors = []
    skip_preexisting('../data/image')
    # extractors += convert_preexisting('../data/image', outdir='../data')
    # extractors += [MinecraftExtractor('minecraft', outdir='../data'), TerrariaExtractor('terraria', outdir="../data")]
    extractors += convert_executables("../executables", outdir='../data')

    samples = ExtractorBase.sample_random(100)
    print([sample.file for sample in samples])
