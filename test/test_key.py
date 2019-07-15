#-*- coding:utf-8 -*-  
""" 
@author:HuHongling

@file: test_key.py 
@time: 2019/07/12
@contact: huhonglin@hwasmart.com
@site:  
@software: PyCharm 

"""
import curses

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)

try:
    while True:
        char = screen.getch()
        if char == ord('q'):
            break
        elif char == curses.KEY_UP:
            print("up")
        elif char == curses.KEY_DOWN:
            print("down")
        elif char == curses.KEY_RIGHT:
            print('right')
        elif char == curses.KEY_LEFT:
            print("left")
        elif char == 10:
            print('enter')
finally:
    curses.nocbreak();
    screen.keypad(0)
    curses.echo()
    curses.endwin()
