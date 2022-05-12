from PIL import Image
import os
import random

# Array List Item
card_4s = [('img/card_4s/' + filename) for filename in os.listdir('img/card_4s/') if os.path.isfile(os.path.join('img/card_4s/', filename))]
card_rateoff = [('img/card_5s/rateoff/' + filename) for filename in os.listdir('img/card_5s/rateoff/') if os.path.isfile(os.path.join('img/card_5s/rateoff/', filename))]
wep_4s = [('img/card_4s/wep_4s/' + filename) for filename in os.listdir('img/card_4s/wep_4s/') if os.path.isfile(os.path.join('img/card_4s/wep_4s/', filename))]
wep_3s = [('img/wep_3s/' + filename) for filename in os.listdir('img/wep_3s/') if os.path.isfile(os.path.join('img/wep_3s/', filename))]

def gacha(inp):
  limited = f"img/card_5s/{inp}.png"

  # Randomizer
  pull= []
  for i in range(9):
    s3=wep_3s[random.randint(0, len(wep_3s)-1)]
    s4=random.choices(
      population=[
        random.choice(card_4s), 
        random.choice(wep_4s)
        ], 
      weights=[70,30], 
      k=1)[0]
    s5r=random.choice(card_rateoff)
    pull.append(
      random.choices(
        population=[s3, s4, limited, s5r], 
        weights=[90, 8, 1, 1], 
        k=1)[0])
  pull.insert(
    random.randint(0, 8), 
    random.choices(
      population=[
        random.choice(card_4s), 
        random.choice(wep_4s)
        ],
      weights=[70,30], 
      k=1)[0])

  # Sorting Array
  for i in range(10):
    if pull[i] in card_4s + wep_4s:
      pull.insert(0, pull.pop(i))
  for i in range(10):
    if pull[i] == limited or pull[i] in card_rateoff:
      pull.insert(0, pull.pop(i))

  # Merge Array & Save Output
  def concatimg(arr):
    new_img = Image.new("RGBA", (1000, 600))
    for j, i in enumerate(arr):
      new_img.paste(Image.open(i), (100*j, 0))
    return new_img
  concatimg(pull).save('test.png')
  return pull