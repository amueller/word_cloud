import array
import numpy as np
from random import Random


def query_integral_image(integral_image, size_x,
                         size_y, random_state):
    
    if isinstance(random_state, Random):
      x = integral_image.shape[0]
      y = integral_image.shape[1]
      hits = 0
      for i in range(x - size_x):
        for j in range(y - size_y):
          area = integral_image[i, j] + integral_image[i + size_x, j + size_y]
          area -= integral_image[i + size_x, j] + integral_image[i, j + size_y]
          if not area: 
            hits += 1
      
      if not hits:
        return None
      
      goal = random_state.randint(0, hits)
      hits = 0
      for i in range(x - size_x):
        for j in range(y - size_y):
          area = integral_image[i, j] + integral_image[i + size_x, j + size_y]
          area -= integral_image[i + size_x, j] + integral_image[i, j + size_y]
          if not area:
            hits += 1
            if hits == goal:
              return i, j
      
    else:
      x = integral_image.shape[1] # width
      y = integral_image.shape[0] # hieght
      fix_x = round(random_state[1])
      fix_y = round(random_state[0])

      center_y = round(fix_y-(size_y/2))
      center_x = fix_x

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
              if not area: #ถ้า not area --> size x < x or size y < y แสดงว่ามีพท แต่ถ้าสมมติมันใหญ่เกินก็ค่อยไปลด font size
                return new_center_x,new_center_y
            except:
              continue
      return None
