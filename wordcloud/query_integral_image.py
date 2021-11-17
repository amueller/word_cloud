import array
import numpy as np

#integral_image = np.zeros((3000, 2000), dtype=np.uint32)
def query_integral_image(integral_image, size_x,
                         size_y, fix_state):
  
    x = integral_image.shape[1] # width
    y = integral_image.shape[0] # hieght
    

    hits = 0
    lis = []
    fix_x = round(fix_state[1])
    fix_y = round(fix_state[0])
    #center_x = round(fix_x-(size_x/2))
    center_y = round(fix_y-(size_y/2))
    center_x = fix_x
    #center_y = fix_y

    if center_x < 0:
      center_x = 0
    if center_y < 0:
      center_y = 0

    for r in range(1,500):
      for x_sign in [-1,1]:
        for r_sign in [-1,1]:
          new_center_x = center_x + (r*r_sign)
          new_center_y = center_y + (r*x_sign)

          try:
            area = integral_image[new_center_x, new_center_y] + integral_image[new_center_x + size_x, new_center_y + size_y]
            area -= integral_image[new_center_x + size_x, new_center_y] + integral_image[new_center_x, new_center_y + size_y]

            if not area: #ถ้า not area --> size x < x or/and size y < y แสดงว่ามีพท แต่ถ้าสมมติมันใหญ่เกินก็ค่อยไปลด font size ใน 
              return new_center_x,new_center_y

          except:
            continue
    return None