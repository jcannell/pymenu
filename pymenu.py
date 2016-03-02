import sys

# Menu level constants
MENU_ROOT   = 1

# Option ID constants
OPT_ID_NULL = 0
OPT_ID_NAVP = 9902
OPT_ID_NAVC = 9903
OPT_ID_NAVE = 9904

class MenuError(Exception):
    """Encounters a menu error, but can recover"""

class MenuCreateError(MenuError):
    """Encountered when a Menu is invalid"""

class MenuEditError(MenuError):
    """Encounters an error editing a menu"""

class MenuNavigateError(MenuError):
    """Encounters an error navigating to/from parent/child menus"""

class MenuOptionError(MenuError):
    """Encounters an error setting or retrieving menu options"""

class MenuRuntimeError(MenuError):
    """Encounters an when running a menu"""

class MenuOption(object):

    def __init__(self, id, text="", selectors=[], fx=None):

        # Validate input
        if id <= OPT_ID_NULL:
            raise MenuOptionError("Option id cannot be zero or negative")
        elif text and not isinstance(text, str):
            raise MenuOptionError("Option text is not a string")
        elif selectors and not isinstance(selectors, list):
            raise MenuOptionError("Option selectors is not a list")
        elif fx and not hasattr(fx, '__call__'):
            raise MenuOptionError("Option function is not callable")
        else:
            self._id        = id
            self._fx        = fx
            self._text      = text
            self._selectors = selectors

    def get_id(self):
        """
        Retrieves the id for a MenuOption
        :return:                       A MenuOption id
        """

        return self._id

    def get_fx(self):
        """
        Retrieves the option function for a MenuOption
        :return:                       A MenuOption function
        """

        return self._fx

    def get_text(self):
        """
        Retrieves the option text for a MenuOption
        :return:                       A MenuOption text string
        """

        return self._text

    def get_selectors(self):
        """
        Retrieves the option selectors for a MenuOption
        :return:                       A MenuOption selectors list
        """

        return self._selectors

    def set_id(self, id):
        """
        Sets the option id for a MenuOption
        :return:                       Nothing
        """
        if id <= OPT_ID_NULL:
            raise MenuOptionError("Option id cannot be zero or negative")
        else:
            self._id = id

    def set_fx(self, fx):
        """
        Sets the option function for a MenuOption
        :return:                       Nothing
        """

        if fx and not hasattr(fx, '__call__'):
            raise MenuOptionError("Option function is not callable")
        else:
            self._fx = fx

    def set_text(self, text):
        """
        Sets the option text for a MenuOption
        :return:                       Nothing
        """

        if text and not isinstance(text, str):
            raise MenuOptionError("Option text is not a string")
        else:
            self._text = text

    def set_selectors(self, selectors):
        """
        Sets the option selectors for a MenuOption
        :return:                       Nothing
        """

        if selectors and not isinstance(selectors, list):
            raise MenuOptionError("Option selectors is not a list")
        else:
            self._selectors = selectors

    def print_opt(self):
        """
        Prints the option text for a MenuOption
        :return:                       Nothing
        """

        print(self.get_text())

class Menu(object):

    def __init__(self, prompt="Menu>", lvl=MENU_ROOT, add_back=False):
        """
        Creates an empty menu
        :param prompt:                 Prompt the menu displays
        :param lvl:                    Level for the new menu
        :param add_back:               Adds an option to navigate to the parent menu
        :return:                       A new Menu object
        """

       # Validate input
        if not isinstance(prompt, str):
            raise MenuCreateError("Menu prompt is not a string")
        elif not isinstance(lvl, int):
            raise MenuCreateError("Menu level is not an integer")
        elif lvl < MENU_ROOT:
            raise MenuCreateError("Menu level is an invalid integer")
        else:
            self._options     = []
            self._child_menus = []
            self._parent_menu = None
            self._prompt      = prompt
            self._lvl         = lvl

        # Create back option if specified
        if add_back and lvl == MENU_ROOT:
            raise MenuCreateError("Menu add_back for MENU_ROOT level menu")
        elif add_back:
            self.add_option(OPT_ID_NAVP, "[b]ack", ["b", "back"], self.nav_parent)
        else:
            pass

    def add_option(self, id, text="", selectors=[], fx=None):
        """
        Adds an option to a menu
        :param id:                     Id for the option
        :param text:                   Text for the option
        :param selectors:              Selectors for the option
        :param fx:                     Function to run for option
        :raise MenuOptionError:        If the option already exists
        :return:                       Nothing
        """

        if self.option_exists(id):
            raise MenuOptionError("Option already exists")
        elif id == OPT_ID_NAVC:
            fx = self.nav_child
        elif id == OPT_ID_NAVP:
            fx = self.nav_parent
        else:
            pass
        self._options.append(MenuOption(id, text, selectors, fx))

    def add_option_obj(self, opt):
        """
        Adds an option to a menu using a MenuOption object
        :param opt:                    A MenuOption object representing the option to add
        :raise MenuOptionError:        If the option already exists
                                       If the option to add isn't of type MenuOption
        :return:                       Nothing
        """

        if self.option_exists(opt.get_id()):
            raise MenuOptionError("Option already exists")
        elif not isinstance(opt, MenuOption):
            raise MenuOptionError("Option is not a MenuOption object")
        else:
            self._options.append(opt)

    def add_options(self, opts):
        """
        Adds a list of options to a menu
        :param opts:                   A list of MenuOption objects
        :raise MenuOptionError:        If options are not in a list
                                       If an option to add isn't of type MenuOption
                                       If an option to add already exists
        :return:                       Nothing
        """

        if isinstance(opts, list):
            for opt in opts:
                if isinstance(opt, MenuOption):
                    if self.option_exists(opt):
                        raise MenuOptionError("Option already exists")
                    else:
                        self._options.append(opt)
                else:
                    raise MenuOptionError("Option is not a MenuOption object")
        else:
            raise MenuOptionError("Options must be given as a list")

    def add_child_menu(self, use_menu=None, link_parent=True):
        """
        Adds a child menu to an existing menu in the form of a
        Menu object. The new child menu has a level that is one
        greater than its parent menu. If use_menu is supplied a Menu
        object, it will be used as the child menu, otherwise a blank
        menu is used. In addition, if link_parent is True, the existing
        parent menu will automatically be added (linked) to the new
        child menu.
        :raise MenuCreateError:        If a child menu already exists
                                       If use_menu is not a Menu object
        :return:                       Nothing
        """

        current_lvl  = self.get_level()
        child_menu_lvl = current_lvl + 1
        if use_menu and use_menu in self.get_child_menus():
            raise MenuCreateError("Child menu already exists")
        if use_menu and not isinstance(use_menu, Menu):
            raise MenuCreateError("Child use_menu is not a Menu object")
        elif use_menu:
            # Enforce correct child level by setting it
            use_menu.set_level(child_menu_lvl)
            if link_parent:
                use_menu.add_parent_menu(self)
            self._child_menus.append(use_menu)
        else:
            # Create a blank menu if one is not supplied
            child_menu = Menu(self.get_prompt(), child_menu_lvl, add_back=True)
            if link_parent:
                child_menu.add_parent_menu(self)
            self._child_menus.append(child_menu)

    def add_parent_menu(self, use_menu=None):
        """
        Adds a parent menu to an existing menu in the form
        of a Menu object. The new parent menu has a level that is one
        less than its parent menu. Note that any attempt to create a parent
        menu for a menu with level MENU_ROOT will raise a MenuCreateError.
        :raise MenuCreateError:        If a parent menu already exists
                                       If use_menu is not a Menu object
                                       If applied to a menu of level MENU_ROOT
        :return:                       Nothing
        """

        current_lvl  = self.get_level()
        parent_menu_lvl = current_lvl - 1
        if self.get_parent_menu():
            raise MenuCreateError("Parent menu already exists")
        elif current_lvl == MENU_ROOT:
            raise MenuCreateError("Parent menu cannot exist on MENU_ROOT menu")
        elif use_menu and not isinstance(use_menu, Menu):
            raise MenuCreateError("Parent use_menu is not a Menu object")
        elif use_menu:
            # Enforce correct child level by setting it
            use_menu.set_level(parent_menu_lvl)
            self._parent_menu = use_menu
        else:
            # Create a blank menu if one is not supplied
            self._parent_menu = Menu(self.get_prompt(), parent_menu_lvl)

    def nav_child(self):
        """
        Navigates to the child menu
        :raise MenuNavigateError:      If no child menu exists
        :return:                       Nothing
        """

        if not self.get_child_menus():
            raise MenuNavigateError("Navigation failed, child menu does not exist")
        else:
            self.get_child_menus().run()

    def nav_parent(self):
        """
        Navigates to the parent menu
        :raise MenuNavigateError:      If no parent menu exists
        :return:                       Nothing
        """

        if not self.get_parent_menu():
            raise MenuNavigateError("Navigation failed, parent menu does not exist")
        else:
            self.get_parent_menu().run()

    def clear_options(self):
        """
        Clears options for a menu
        :return:                       Nothing
        """

        self._options = []

    def edit_option(self, id, text="", selectors=[], fx=None):
        """
        Edit a menu option. Note that only the option id is requried.
        If other option parameters are not explicitly set when called,
        edit_option, will use the existing option parameters.
        :param id:                     The id for the menu option to edit
        :param text:                   The text for the option to display
        :param selectors:              The list of selectors which trigger the option function
        :param fx:                     The function for the option to run
        :raise MenuOptionError:        If the option does not exist
        :return:                       Nothing
        """

        if not self.option_exists(id):
            raise MenuOptionError("Option does not exist")
        else:
            opt = self.get_option_by_id(id)

        # Use the existing option values if new ones are not explicitly set
        if not text:
            text = opt.get_text()
        if not selectors:
            selectors = opt.get_selectors()
        if not fx:
            fx = opt.get_fx()

        opt.set_fx(fx)
        opt.set_text(text)
        opt.set_selectors(selectors)

    def get_level(self):
        """
        Retrieves a menu level
        :return:                       The menu level
        """

        return self._lvl

    def get_option_by_id(self, id):
        """
        Retrieves a menu option using the supplied option id
        :param id:                     The id used to retrieve the option
        :return:                       The requested option, or None if it doesn't exist
        """

        if self.option_exists(id):
            # Should only be one item on the list, so pop() should succeed
            try:
                return [o for o in self.get_options() if o.get_id() == id].pop()
            except IndexError:
                return None
        else:
            return None

    def get_options(self):
        """
        Retrieves the current options for a Menu object
        :return:                       List of menu options
        """

        return self._options

    def get_prompt(self):
        """
        Retrieves the current prompt for a Menu object
        :return:                       A menu prompt
        """

        return self._prompt

    def get_selection(self):
        """
        Retrieves the user menu selection from keyboard input
        :return:                       A user selection
        """

        sys.stdout.write(self.get_prompt())
        selection = sys.stdin.readline().rstrip("\n")
        sys.stdin.flush()
        sys.stdout.flush()

        return selection

    def get_child_menus(self):
        """
        Retrieves a menu's child menus
        :return:                       List of child Menu objects
        """

        return self._child_menus

    def get_parent_menu(self):
        """
        Retrieves a menu's parent menu
        :return:                       A Menu object, or None if it doesn't exist
        """

        return self._parent_menu

    def option_exists(self, id):
        """
        Checks if an option exists
        :param id:                     Option id to check
        :return:                       True if an option exists, False otherwise
        """

        if [o for o in self.get_options() if o.get_id() == id]:
            return True
        else:
            return False

    def remove_child_menu(self):
        """
        Removes a child menu from a menu
        :return:                       Nothing
        """

        self._child_menu = None

    def remove_parent_menu(self):
        """
        Removes a parent menu from a menu
        :return:                       Nothing
        """

        self._parent_menu = None

    def remove_option(self, id):
        """
        Removes a menu option using the supplied option id
        :param id:                     An id for the option to remove
        :return:                       Nothing
        """

        if self.option_exists(id):
            try:
                self._options.remove(self.get_option_by_id(id))
            except IndexError:
                pass

    def run(self):
        """
        Runs a menu, allowing a user to make selections
        :raise MenuRuntimeError:       If the menu has no options
                                       If the selected option has no function
        :return:                       Nothing
        """
        option_fx       = None
        opt_exit        = None
        opt_parent      = None
        options         = self.get_options()
        HAS_EXIT        = False
        HAS_PARENT      = False

        if not options:
            raise MenuRuntimeError("Called menu has no options")

        # Print options to the screen
        for option in options:
            if option.get_id() == OPT_ID_NAVP:
                HAS_PARENT = True
                opt_parent = option
                continue
            if option.get_id() == OPT_ID_NAVE:
                HAS_EXIT = True
                opt_exit = option
                continue
            else:
                option.print_opt()
        if HAS_PARENT:
            opt_parent.print_opt()
        if HAS_EXIT:
            opt_exit.print_opt()
        print("")

        while True:
            user_sel = self.get_selection()

            # Combine all option selector lists into one list
            sel_subs = [s.get_selectors() for s in options]

            # Then flatten the sublists into a list
            sel_all = [item for sublist in sel_subs for item in sublist]

            if user_sel in sel_all:
                break

        # print a blank line if success
        print("")

        # for every option
        for option in options:
            if option_fx:
                break

            if user_sel in option.get_selectors():
                option_fx = option.get_fx()
                break

        if option_fx:
            option_fx()
        else:
            raise MenuRuntimeError("Called menu option has no function")

    def set_level(self, lvl):
        """
        Sets the level for a Menu object. Note that if another menu exists within
        the instance of the caller, this function will fail. Note that a root-level
        menu shouild be set to MENU_ROOT.
        :param lvl:                    A valid menu level
        :raise MenuEditError:          If an illegal lvl is given
        :return:                       Nothing
        """

        if not isinstance(lvl, int):
            raise MenuEditError("Menu level is not an integer")
        if lvl < MENU_ROOT:
            raise MenuEditError("Menu level is an invalid integer")

        if self.get_parent_menu() and self.get_parent_menu().get_level() >= lvl:
            raise MenuEditError("Menu level lower than the parent menu level")
        if self.get_child_menus() and [l for l in self.get_child_menus() if l <= lvl]:
            raise MenuEditError("Menu level higher than the child menu level")

        self._lvl = lvl

    def set_prompt(self, prompt):
        """
        Sets the prompt for a Menu object
        :param prompt:                 A string to use as a prompt
        :raise MenuEditError:          If prompt is not a string
        :return:                       Nothing
        """

        if not isinstance(prompt, str):
            raise MenuEditError("Menu prompt is not a string")
        else:
            self._prompt = prompt