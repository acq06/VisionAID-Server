BAYBAYIN_TRANSLATION = {
    "ᜀ": "A",
    "ᜁ": "E/I",
    "ᜂ": "O/U",
    "ᜊ᜔": "B",
    "ᜊ": "Ba",
    "ᜊᜒ": "Be/Bi",
    "ᜊᜓ": "Bo/Bu",
    "ᜃ᜔": "K",
    "ᜃ": "Ka",
    "ᜃᜒ": "Ke/Ki",
    "ᜃᜓ": "Ko/Ku",
    "ᜇ᜔": "D",
    "ᜇ": "Da",
    "ᜇᜒ": "De/Di",
    "ᜇᜓ": "Do/Du",
    "ᜇ᜔": "R",
    "ᜇ": "Ra",
    "ᜇᜒ": "Re/Ri",
    "ᜇᜓ": "Ro/Ru",
    "ᜄ᜔": "G",
    "ᜄ": "Ga",
    "ᜄᜒ": "Ge/Gi",
    "ᜄᜓ": "Go/Gu",
    "ᜑ᜔": "H",
    "ᜑ": "Ha",
    "ᜑᜒ": "He/Hi",
    "ᜑᜓ": "Ho/Hu",
    "ᜎ᜔": "L",
    "ᜎ": "La",
    "ᜎᜒ": "Le/Li",
    "ᜎᜓ": "Lo/Lu",
    "ᜋ᜔": "M",
    "ᜋ": "Ma",
    "ᜋᜒ": "Me/Mi",
    "ᜋᜓ": "Mo/Mu",
    "ᜈ᜔": "N",
    "ᜈ": "Na",
    "ᜈᜒ": "Ne/Ni",
    "ᜈᜓ": "No/Nu",
    "ᜉ᜔": "P",
    "ᜉ": "Pa",
    "ᜉᜒ": "Pe/Pi",
    "ᜉᜓ": "Po/Pu",
    "ᜐ᜔": "S",
    "ᜐ": "Sa",
    "ᜐᜒ": "Se/Si",
    "ᜐᜓ": "So/Su",
    "ᜆ᜔": "T",
    "ᜆ": "Ta",
    "ᜆᜒ": "Te/Ti",
    "ᜆᜓ": "To/Tu",
    "ᜏ᜔": "W",
    "ᜏ": "Wa",
    "ᜏᜒ": "We/Wi",
    "ᜏᜓ": "Wo/Wu",
    "ᜌ᜔": "Y",
    "ᜌ": "Ya",
    "ᜌᜒ": "Ye/Yi",
    "ᜌᜓ": "Yo/Yu",
    "ᜅ᜔": "Ng",
    "ᜅ": "Nga",
    "ᜅᜒ": "Nge/Ngi",
    "ᜅᜓ": "Ngo/Ngu",
}


def translate_word(word):
    translated_word = ""
    for c in word:
        if c in BAYBAYIN_TRANSLATION:
            c = BAYBAYIN_TRANSLATION[c]
        translated_word += c

    return translated_word


def rectangles_overlap(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    return not (
        x1 + w1 < x2  # rect1 is to the left of rect2
        or x2 + w2 < x1  # rect2 is to the left of rect1
        or y1 + h1 < y2  # rect1 is above rect2
        or y2 + h2 < y1
    )  # rect2 is above rect1


def rectangle_inside(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    return x1 >= x2 and y1 >= y2 and x1 + w1 <= x2 + w2 and y1 + h1 <= y2 + h2


def refine_result_boxes(result):
    boxes = []
    for box in result.boxes:
        x, y, w, h = box.xywh[0]
        conf = box.conf

        # Initialize a flag to determine if the current box is redundant
        redundant = False

        for i, existing_box in enumerate(boxes):
            ex, ey, ew, eh, econf = existing_box

            # Calculate IoU (Intersection over Union) to check overlap
            intersection_x = max(
                0, min(x + w / 2, ex + ew / 2) - max(x - w / 2, ex - ew / 2)
            )
            intersection_y = max(
                0, min(y + h / 2, ey + eh / 2) - max(y - h / 2, ey - eh / 2)
            )
            intersection_area = intersection_x * intersection_y
            union_area = w * h + ew * eh - intersection_area

            iou = intersection_area / union_area if union_area > 0 else 0

            # Check if the current box is inside the existing box
            is_inside = (
                x - w / 2 >= ex - ew / 2
                and x + w / 2 <= ex + ew / 2
                and y - h / 2 >= ey - eh / 2
                and y + h / 2 <= ey + eh / 2
            )

            # Check if the existing box is inside the current box
            contains_existing = (
                ex - ew / 2 >= x - w / 2
                and ex + ew / 2 <= x + w / 2
                and ey - eh / 2 >= y - h / 2
                and ey + eh / 2 <= y + h / 2
            )

            if iou > 0.5 or is_inside or contains_existing:
                # Remove the box with the lower confidence score
                if conf > econf:
                    boxes[i] = [x, y, w, h, conf]
                redundant = True
                break

        # If the current box is not redundant, add it to the list
        if not redundant:
            boxes.append([x, y, w, h, conf])

    return boxes


def redefine_boxes(boxes):
    bboxes = []
    for box in boxes:
        x, y, w, h, conf = box
        xmin = x - (w / 2)
        xmax = x + (w / 2)
        ymin = y - (h / 2)
        ymax = y + (h / 2)

        bboxes.append([xmin, ymin, xmax, ymax])

    return bboxes


def recursive_xy_cut(bboxes):
    def split_by_axis(bboxes, axis):
        grouped = []
        current_group = []
        for i, box in enumerate(bboxes):
            if not current_group:
                current_group.append(box)
            else:
                if is_overlap(current_group[-1], box, axis):
                    current_group.append(box)
                else:
                    grouped.append(current_group)
                    current_group = [box]
        if current_group:
            grouped.append(current_group)
        return grouped if len(grouped) > 1 else []

    def is_overlap(box1, box2, axis):
        if axis == 0:  # Vertical axis (x)
            return box1[2] >= box2[0]
        elif axis == 1:  # Horizontal axis (y)
            return box1[3] >= box2[1]

    if len(bboxes) <= 1:
        return bboxes

    # Sort and try vertical cut
    bboxes.sort(key=lambda box: box[0])
    vertical_cut = split_by_axis(bboxes, axis=0)

    if vertical_cut:
        sorted_groups = [recursive_xy_cut(group) for group in vertical_cut]
    else:
        # Sort and try horizontal cut
        bboxes.sort(key=lambda box: box[1])
        horizontal_cut = split_by_axis(bboxes, axis=1)
        if horizontal_cut:
            sorted_groups = [recursive_xy_cut(group) for group in horizontal_cut]
        else:
            return bboxes  # Base case: return sorted group

    # Flatten sorted groups
    return [box for group in sorted_groups for box in group]


def split_by_axis(bboxes, axis):
    # Group bounding boxes based on axis overlap
    grouped = []
    current_group = []
    for i, box in enumerate(bboxes):
        if not current_group:
            current_group.append(box)
        else:
            if is_overlap(current_group[-1], box, axis):
                current_group.append(box)
            else:
                grouped.append(current_group)
                current_group = [box]
    if current_group:
        grouped.append(current_group)

    return grouped if len(grouped) > 1 else []


def is_overlap(box1, box2, axis):
    # Check overlap between two bounding boxes along a specified axis
    if axis == 0:  # Vertical axis (x)
        return box1[2] >= box2[0]
    elif axis == 1:  # Horizontal axis (y)
        return box1[3] >= box2[1]
