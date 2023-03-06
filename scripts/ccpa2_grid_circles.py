import numpy as np
import cv2
import sys
import random as rng
import pyperclip
from matplotlib import pyplot as plt


###
###
###notes first image assay (image(1).png) is in BGR format!
###
###


###static stored locations of image(1).png grid that has both A/B images
#STATIC_GRID_DOT_LOCATIONS = [(96, 455), (140, 455), (183, 455), (229, 456), (273, 456), (318, 456), (363, 455), (407, 456), (453, 456), (498, 455), (542, 454), (586, 454), (585, 502), (542, 500), (497, 501), (452, 500), (408, 499), (362, 499), (317, 500), (274, 500), (228, 500), (183, 501), (139, 500), (95, 500), (94, 546), (139, 545), (184, 546), (228, 546), (275, 545), (318, 546), (363, 545), (408, 545), (452, 545), (497, 546), (543, 545), (585, 544), (585, 588), (541, 590), (497, 590), (451, 588), (409, 589), (363, 590), (318, 590), (274, 589), (229, 589), (186, 590), (139, 589), (93, 591), (95, 633), (138, 634), (184, 634), (231, 635), (274, 633), (319, 633), (362, 636), (408, 633), (452, 633), (496, 634), (540, 633), (585, 633), (586, 678), (541, 677), (496, 677), (453, 679), (407, 677), (360, 678), (317, 677), (272, 678), (229, 678), (183, 679), (140, 679), (95, 679), (94, 724), (140, 723), (183, 724), (229, 724), (273, 722), (318, 724), (365, 724), (409, 724), (451, 722), (498, 725), (540, 723), (586, 723), (585, 766), (539, 766), (497, 768), (452, 766), (407, 766), (362, 767), (316, 766), (274, 766), (229, 766), (186, 767), (139, 767), (95, 767)]

STATIC_GRID_DOT_LOCATIONS = [(353, 861), (407, 860), (456, 860), (506, 862), (564, 863), (617, 864), (671, 860), (726, 863), (776, 863), (832, 862), (883, 864), (939, 865), (350, 964), (405, 966), (456, 966), (510, 967), (565, 966), (616, 968), (669, 967), (723, 966), (778, 969), (828, 967), (882, 969), (936, 967), (353, 1074), (407, 1076), (456, 1074), (511, 1075), (563, 1075), (618, 1077), (672, 1077), (723, 1077), (777, 1074), (830, 1073), (884, 1075), (938, 1076), (352, 1180), (407, 1175), (458, 1178), (510, 1178), (564, 1179), (618, 1179), (670, 1178), (724, 1180), (774, 1179), (829, 1181), (884, 1179), (937, 1178)]

#used to create ROI
GRID_BOX_SPACING=21

#(row, column) grid size in this case A-H and 1-12
GRID_SIZE = (8, 12)

_paused = False
_click_coordinates = list()
_mouse_coordinates = None
_mouse_scroll_radius = 12
_rotate_angle = 0.0
_left_click_is_pressed = False
_blue_memory = [0 for x in STATIC_GRID_DOT_LOCATIONS]

def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result

def crop(img, x, y, w, h):
    
    return img[y:y+h, x:x+w]

def distance(a, b): 
    
    return int(((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5)

def calculate_blue_hsv(frame, lab, top_left, bottom_right):
    
    try:
    
        #get key press to check if we want to plot B distribution
#        key_press = cv2.waitKey(1) & 0xFF

        y1 = top_left[1]

        x1 = top_left[0]

        y2 = bottom_right[1]

        x2 = bottom_right[0]
        
        roi = lab[y1:y2, x1:x2]

        #print(roi.shape)
        #calculate length and width
        w = len(roi[0])
        h = len(roi)
        
        roi = create_circular_mask(roi, (0, 0, w, h))

        radius = int(min(w,h)/2)

        #calculate total area of roi
        area = 3.141592 * radius * radius
        
        #uncomment to see the individual rois
        #cv2.imshow("dots", roi)

        #lumin, green->yellow, blue->yellow
#        lower_range = np.array([0, 0, 0])
#        upper_range = np.array([255, 255, 128])
#        mask = cv2.inRange(roi, lower_range, upper_range)
#               
        a = np.argwhere(roi[:,:,2] >= 0)
        b = np.argwhere(roi[:,:,2] <= 128)
        c = np.argwhere(roi[:,:,0] > 128)
        d = np.argwhere(roi[:,:,0] < 255)

        aset = set([tuple(x) for x in a])
        bset = set([tuple(x) for x in b])
        cset = set([tuple(x) for x in c])
        dset = set([tuple(x) for x in d])
        
        a = np.array([x for x in aset & bset & cset & dset])
        
        score = 0
#        for i in range(0,width):
#            for j in range(0,length):
#                pixel = roi[i][j]
#                #check if Luminosity is between 128-255
#                #check if B value is between 0-128
#                if ((pixel[2] >= 0) and (pixel[2] <= 128)) and (pixel[0] > 128) and (pixel[0] < 255):
#                    score = score + (255-pixel[0])
        
        for (x,y) in a:
            pixel = roi[x][y]
            score = score + (255-pixel[0])
            
        #uncomment to see the masked calculation area
        #cv2.imshow("dots", mask)
        
        count = int(score / area)
        #count all blue pixels and normalize by area of roi
        #count = int((np.count_nonzero(mask) / area) * 255)
        
#        if key_press == ord('r'):
#            full_mask = cv2.inRange(lab, lower_range, upper_range)
#            cv2.imshow("lab", full_mask)
#            
#        if key_press == ord('e'):
#            #histogram of pixel intensity values
#            plt.hist(roi[:,:, 2].ravel(), 256, [0,256])
#            plt.show()
            
        return count
    
    except Exception as e:
        
        print(e)
        
        return 0
    
def create_circular_mask(frame, rect):
    mask = np.zeros(frame.shape, dtype=np.uint8)
    x,y,w,h = rect
    center = (int(x + w/2), int(y + h/2))
    radius = int(min(w,h)/2)
    cv2.circle(mask,center,radius,(255,255,255),-1,cv2.LINE_AA)
    return cv2.bitwise_and(frame,mask)

def click_callback(event, x, y, flags, param):
    
    global _left_click_is_pressed
    global _rotate_angle
    global _click_coordinates
    global _mouse_coordinates
    global _mouse_scroll_radius
    global frame
    
    #get a key pressed during a mouse event
    key = cv2.waitKey(1) & 0xFF
    
    if event == cv2.EVENT_LBUTTONDOWN:
        
        _left_click_is_pressed = True
        
        _click_coordinates.append((x,y))
        
        print(_click_coordinates)

    elif event == cv2.EVENT_LBUTTONUP:
        
        _left_click_is_pressed = False
        
    _mouse_coordinates = (x,y)

def build_grid(mouse_coordinates, grid):
    
    #make list of dot locations relative to mouse coordinates using the param grid spacing
    local_coords = []
    delta_x = 0
    delta_y = 0
    rows = len(grid)
    cols = len(grid[0])
    size = rows*cols
    for index, dot in enumerate(grid):
        
        if index == 0:
            
            local_coords.append(mouse_coordinates)
            
        else:
            
            last_point = index - 1
            
            grid_x = grid[index][0]
            last_grid_x = grid[last_point][0]
            grid_y = grid[index][1]
            last_grid_y = grid[last_point][1]
                             
            if grid_x > last_grid_x:
                
                delta_x = delta_x + abs(last_grid_x - grid_x)
            
            else:
                
                delta_x = delta_x - abs(grid_x - last_grid_x)
                
            if grid_y > last_grid_y:
                
                delta_y = delta_y + abs(grid_y - last_grid_y)
                
            else:
                
                delta_y = delta_y - abs(last_grid_y - grid_y)
                                
            #append relative location, (y,x) for row column format
            local_coords.append((mouse_coordinates[0]+delta_x, mouse_coordinates[1]+delta_y))
    
    return local_coords

def render_dynamic(frame, lab, coords, grid):
    
    global _blue_memory
    
    frame = rotate_image(frame, _rotate_angle)
    lab = rotate_image(lab, _rotate_angle)
    
    layer = None
    
    local_coords = build_grid(coords, STATIC_GRID_DOT_LOCATIONS)
    
    #draw the roi for each coordinate in the static grid
    #also use calculate_blue to analyze the amount of blue in the ROI
    for index, coordinate in enumerate(local_coords):
            
        top_left = (coordinate[0]-GRID_BOX_SPACING, coordinate[1]-GRID_BOX_SPACING)
        bottom_right = (coordinate[0]+GRID_BOX_SPACING, coordinate[1]+GRID_BOX_SPACING)

        #first is top left, second is bottom right corners
        #cv2.rectangle(frame, top_left, bottom_right, (0,255,0), 1)

        #mask = np.zeros(frame.shape, dtype=np.uint8)
        x = top_left[0]
        y = top_left[1]
        w = abs(bottom_right[0] - x)
        h = abs(bottom_right[1] - y)
        
        center = (int(x + w/2), int(y + h/2))
        radius = int(min(w,h)/2)
        cv2.circle(frame, center,radius,(0,255,0),1,cv2.LINE_AA)
        #cv2.imshow("dot", create_circular_mask(frame, (x1, y1, abs(x2-x1), abs(y2-y1))))

        if _left_click_is_pressed:
            
            blueness = calculate_blue_hsv(draw_layer, lab, top_left, bottom_right)

            _blue_memory[index] = blueness
            
            pyperclip.copy("Pixel Blueness Scoring\n" + "\n".join(list(map(lambda x: str(x), _blue_memory))))
            
#            cv2.putText(image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])

        cv2.putText(frame, str(_blue_memory[index]), top_left, cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 1)

    return frame

windowName = "CCP Assay {}".format(sys.argv[1])
cv2.namedWindow(windowName)
cv2.setMouseCallback(windowName, click_callback)

file_name = sys.argv[1]

print("Loading " + file_name)

mouseLabel = (0,255,255)
hullLabel = (0,0,255)
bbox = None

frame = cv2.imread(file_name)

print("Size " + str(frame.shape[0]) + " " + str(frame.shape[1]))

frame = cv2.pyrDown(frame)
frame = cv2.pyrDown(frame)
frame = cv2.pyrDown(frame)

print("Size " + str(frame.shape[0]) + " " + str(frame.shape[1]))

while cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) >= 1:
        
    #convert color space to LAB
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        
            cv2.destroyAllWindows()
            
            break
    
    while cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) >= 1:

        key_press = cv2.waitKey(1) & 0xFF
        
        if key_press == ord(' '):
            
            _paused = not _paused
            
        elif key_press in [ord('q'), 27]:
            
            cv2.destroyAllWindows()

            break

        elif key_press == ord('1'):
            
            _rotate_angle = _rotate_angle - 1.0
        
        elif key_press == ord('2'):
            
            _rotate_angle = _rotate_angle + 1.0
            
        if _paused:
            
            bbox = cv2.selectROI("frame", frame, False, False)
            
            _paused = not _paused
            
        if not _paused:

            if frame is None:
                
                break
                
            if bbox is not None:
                
                frame = crop(frame, *bbox)
                
                bbox = None
                
                print("Cropped!")
                
                print(frame.shape)
                
            #render clicks using addWeighted to combine layers
            draw_layer = frame.copy()
            
            if _mouse_coordinates:
            
                draw_layer = render_dynamic(draw_layer, lab, _mouse_coordinates, STATIC_GRID_DOT_LOCATIONS)
                                                                                      
            cv2.imshow(windowName, draw_layer)

cv2.destroyAllWindows()