#!/usr/bin/python
import glob
import pyautogui as pag
import time


class FindAndClick:
    digits = [i for i in '0123456789']
    prev = []
    found = False

    def __init__(self, image, click='l', x_adjust=0, y_adjust=0):
        self.image = 'images/' + image
        image_attributes = {
            'image': image,
            'click': click,
            'x_adjust': x_adjust,
            'y_adjust': y_adjust,
            'after right click': False,
        }
        if len(self.prev) > 0:
            if self.prev[0]['click'] == 'r':
                image_attributes['after right click'] = True

        if image_attributes['image'] == 'qualifiers.png':
            # Don't add qualifiers to the previous images.
            pass
        else:
            images = []
            for item in self.prev:
                images.append(item['image'])

            if image_attributes['image'] not in images:
                self.prev.insert(0, image_attributes)
            else:
                pass

        if len(self.prev) > 6:
            # Only store previous 5 images. 6 images including the current image at index 0.
            self.prev.pop(-1)

        self.click = click
        self.x_adjust = x_adjust
        self.y_adjust = y_adjust
        # Find the image
        self.find_and_click()

    def find_and_click(self):
        button = pag.locateOnScreen(self.image, confidence=0.9)

        if button is None and self.image[-5] in self.digits:
            button, self.found, not_original_image = self.iter_image()
            print('Iterated and changed:', self.prev[0]['image'], 'to:', not_original_image)
            self.prev[0]['image'] = not_original_image
            self.image = 'images/' + not_original_image

        counter = 0
        while not self.found:
            if counter == 50:
                print(f'Tried for 10 seconds to look for {self.image} and failed. Looking for blocker.')
                cleared, images_added_to_prev = self.search_blockers()
                if cleared:
                    print("It's been cleared!")
                    try:
                        button = pag.locateOnScreen(self.image, confidence=0.9)
                        button_point = pag.center(button)
                        break
                    except TypeError:

                        # if self.prev[0]['after right click']:
                        #
                        #     # Reset on qualifiers
                        #     print('Reseting on qualifiers...')
                        #     FindAndClick('qualifiers.png')
                        #     # Remove qualifiers from FindAndClick.prev
                        #     index = 1 + images_added_to_prev
                        # else:
                        if images_added_to_prev != 0:
                            index = images_added_to_prev
                            print(self.prev)
                            print('Looking for previous image:', self.prev[index])
                            # Make the button the previous image.
                            recursion_find = FindAndClick(self.prev[index]['image'], self.prev[index]['click'],
                                                          self.prev[index]['x_adjust'],
                                                          self.prev[index]['y_adjust'])
                            recursion_find = FindAndClick(self.prev[index-1]['image'], self.prev[index-1]['click'],
                                                          self.prev[index-1]['x_adjust'],
                                                          self.prev[index-1]['y_adjust'])
                            self.image = recursion_find.image
                            self.found = True
                        else:
                            print('Waiting for', self.image)
                            while pag.locateOnScreen(self.image, confidence=0.9) is None:
                                pass
                            button = pag.locateOnScreen(self.image, confidence=0.9)
                            break
                else:
                    print(f'Could not unblock {self.image}.')
                    print(f'Going to wait for {self.image} to become unblocked.')
                    while button is None:
                        try:
                            button = pag.locateOnScreen(self.image,
                                                        confidence=0.8)  # Is Nonetype if it can't find image
                            pag.center(button)  # This line throws error if the image doesn't exist
                            self.found = True
                        except:
                            time.sleep(1)

            try:
                button = pag.locateOnScreen(self.image, confidence=0.8)
                pag.center(button)
                self.found = True
            except:
                # Takes about 0.2 seconds to try to locate an image that's not on the screen.
                if counter % 5 == 0:
                    print(f"Image {self.image} not found. Trying again.")
                counter += 1

        button_point = pag.center(button)
        if self.click == 'r':
            pag.rightClick(button_point.x + self.x_adjust, button_point.y + self.y_adjust)
        else:
            pag.click(button_point.x + self.x_adjust, button_point.y + self.y_adjust)

    def iter_image(self):
        mypath = 'images/'
        length = len(self.image)
        split_point = length - 5

        # Detect amount of files in /images that share the same name besides the digit before ".png"
        file_counter = len(glob.glob1(mypath, self.image[7:split_point] + "*.png"))
        for i in range(1, file_counter + 1):
            next_image = self.image[:split_point] + f'{i}.png'
            print('searching for', next_image)
            button = pag.locateOnScreen(next_image)
            if button is not None:
                print('found the above button^')
                return button, True, next_image[7:]
            elif i == file_counter:
                print(f"Couldn't find {self.image} or its variations. Going to wait for {self.image}")
                return pag.locateOnScreen(self.image), False, self.image[7:]

    def search_blockers(self):
        cleared = False
        print('Searching for blockers...')
        counter = 0
        images_added_to_prev = 0
        while not cleared:
            dell_command_update = pag.locateOnScreen('images/mini_remind_later.png')
            im_error = pag.locateOnScreen('images/error.png')
            mini_ok = pag.locateOnScreen('images/mini_ok.png')

            if counter == 3:
                print('Cannot find error messages. Exiting')
                return True, 0
            elif dell_command_update is not None:
                print('found dell_command_update:', dell_command_update)

                FindAndClick('mini_remind_later.png')
                cleared = True
                images_added_to_prev = 1
                return cleared, images_added_to_prev
            elif im_error is not None:
                print('found im_error:', im_error)
                FindAndClick('mini_ok.png')
                FindAndClick('mini_delete.png')
                FindAndClick('mini_yes.png')
                cleared = True
                images_added_to_prev = 3
                return cleared, images_added_to_prev
            elif mini_ok is not None:
                print('found mini_ok', mini_ok)
                if self.prev[0]['after right click']:
                    images_added_to_prev = 2
                else:
                    images_added_to_prev = 1

                FindAndClick('mini_ok.png')
                cleared = True

                return cleared, images_added_to_prev

            counter += 1

        return cleared, images_added_to_prev


def main():
    FindAndClick('mdn_button1.png')
    print(FindAndClick.prev)


if __name__ == '__main__':
    pass
