#!/usr/bin/env python

import sys
import menu

def hello():
    print('Hello!')

def dudes():
    print('Dudes!')

def cleanup():
    # Perform some cleanup here
    sys.exit(0)

c_menu1 = menu.Menu(prompt="Interrogate>", lvl=2, add_back=True)
c_menu1.add_option(1, "[l]ist processes", ["l", "lp", "list"])
c_menu1.add_option(2, "[n]etwork connections", ["n", "nc", "network"])
c_menu1.add_option(menu.OPT_ID_NAVE, "[q]uit", ["q", "quit"], cleanup)

c_menu2 = menu.Menu(prompt="Interrogate>", lvl=2, add_back=True)
c_menu2.add_option(1, "[d]ll list", ["d", "dll", "list"])
c_menu2.add_option(menu.OPT_ID_NAVE, "[q]uit", ["q", "quit"], cleanup)

r_menu = menu.Menu(prompt="Interrogate>")
r_menu.add_option(1, "[s]urvey target", ["s", "survey"], c_menu1.run)
r_menu.add_option(2, "[e]xamine process", ["e", "examine"], c_menu2.run)
r_menu.add_option(menu.OPT_ID_NAVE, "[q]uit", ["q", "quit"], cleanup)

# m_root.add_child_menu()
# m_child = m_root.get_child_menu()
# m_child.add_option(1, "[d]ogs", ["d", "dogs"])
# m_child.add_option(2, "[c]ats", ["c", "cats"])
# m_child.add_option(menu.OPT_ID_NAVE, "[e]xit", ["e", "exit"], cleanup)

r_menu.add_child_menu(c_menu1)
r_menu.add_child_menu(c_menu2)
r_menu.run()