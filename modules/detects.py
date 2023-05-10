import random


def image_detect(image, *args, **kwargs):
    sections = []
    section_labels = ["person", "tv"]
    for a in range(2):
        x = random.randint(0, image.shape[1])
        y = random.randint(0, image.shape[0])
        w = random.randint(0, image.shape[1] - x)
        h = random.randint(0, image.shape[0] - y)
        sections.append(((x, y, x + w, y + h), section_labels[a]))
    return (image, sections)

def video_detect(video, *args, **kwargs):
    return (video,)