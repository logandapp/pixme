from pixme.image.ImageData import ImageData
from PIL import Image

if __name__ == '__main__':
    FILE = '../data/image/Furfsky Reborn/compactor.png'
    image = ImageData(FILE)
    images = image.create_tiles()
    for i, tile in enumerate(images):
        Image.fromarray(tile).save(f'{i}.png')
