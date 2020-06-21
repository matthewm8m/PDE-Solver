import pickle
import curses
from curses import wrapper
from abc import ABC, abstractmethod
from enum import IntEnum
import os.path

# TODO: Use typing.
# TODO: Make sure that choice input stays on screen.


class ScreenColor(IntEnum):
    TOOLBAR = 1
    FORM = 2


class ProgramState():
    def __init__(self):
        # Initialize dictionaries of all objects.
        self.models = dict()
        self.grids = dict()
        self.solvers = dict()
        self.simulations = dict()

    def save(self, path='data.dat'):
        # Dump all the object information to a file.
        file = open(path, 'wb')
        pickler = pickle.Pickler(file)
        pickler.dump({
            'models': self.models,
            'grids': self.grids,
            'solvers': self.solvers,
            'simulations': self.simulations
        })
        file.close()

    def load(self, path='data.dat'):
        # Check that file actually exists.
        if os.path.exists(path):
            # Load all the object information from a file.
            file = open(path, 'rb')
            unpickler = pickle.Unpickler(file)
            data = unpickler.load()
            file.close()

            # Set the appropriate fields.
            self.models = data['models']
            self.grids = data['grids']
            self.solvers = data['solvers']
            self.simulations = data['simulations']


class Component(ABC):
    def __init__(self, screen, y, x):
        # Curses screen parameters.
        rows, cols = screen.getmaxyx()
        self.screen = screen
        self.loc = (y % rows, x % cols)

    @abstractmethod
    def draw(self):
        pass


class ChoiceComponent(Component):
    def __init__(self, screen, y, x, options, escapes=(), lsel='[', rsel=']'):
        super().__init__(screen, y, x)

        # Choice string parameters.
        self.options = options
        self.escapes = escapes
        self.lsel = lsel
        self.rsel = rsel

        # Active choice selection.
        self.choice = 0 if options else None

    def draw(self):
        # Iterate over each of the options and render them row by row.
        row, col = self.loc
        self.screen.attron(curses.color_pair(ScreenColor.FORM))
        for option in self.options:
            self.screen.addstr(row, col, f"{self.lsel} {self.rsel} {option}")
            row += 1
        self.screen.attroff(curses.color_pair(ScreenColor.FORM))

        # Set the cursor to the position of the selected option.
        if self.choice is not None:
            self.screen.move(self.loc[0] + self.choice,
                             self.loc[1] + len(self.lsel))

    def input(self):
        # Get a key from the user.
        key = self.screen.getch()

        # If key any of the escape keys, immediately
        # return the escape code.
        if key in self.escapes:
            return key

        # If there are no choices, do not worry about updating the
        # selected choice.
        if self.options:
            # If key is enter key, return the choice currently selected
            # and reset the choices.
            if key == ord('\n'):
                choice = self.choice
                self.choice = 0 if self.options else None
                return choice, self.options[choice]
            # If key is arrow key, update choice respectively and
            # return None to indicate that a choice has not been made.
            # Up    - Backward one choice.
            # Down  - Forward one choice.
            # Left  - First choice.
            # Right - Last choice.
            elif key == curses.KEY_UP:
                self.choice = max(0, self.choice - 1)
                return None
            elif key == curses.KEY_DOWN:
                self.choice = min(len(self.options) - 1, self.choice + 1)
                return None
            elif key == curses.KEY_LEFT:
                self.choice = 0
                return None
            elif key == curses.KEY_RIGHT:
                self.choice = len(self.options) - 1
                return None
        return None


class ToolbarComponent(Component):
    def __init__(self, screen, y, x, keys, sep='-', div='|'):
        super().__init__(screen, y, x)

        # Key combination parameters.
        self.keys = keys
        self.sep = sep
        self.div = div

    def draw(self):
        # Construct the string representation of the toolbar.
        string = ""
        index = 0
        for key, text in self.keys.items():
            index += 1
            string += f" {key} {self.sep} {text} "
            if index != len(self.keys):
                string += self.div

        # Add whitespace to stretch to the edge of the screen.
        _, cols = self.screen.getmaxyx()
        row, col = self.loc
        string = string.ljust(cols - col - 1)

        # Draw the string to the page.
        self.screen.attron(curses.color_pair(ScreenColor.TOOLBAR))
        self.screen.addstr(row, col, string)
        self.screen.insch(row, cols - 1, ' ')
        self.screen.attroff(curses.color_pair(ScreenColor.TOOLBAR))


class Page(ABC):
    def __init__(self, screen, state):
        # Set the screen and components.
        self.screen = screen
        self.components = []

        # Set the program state.
        self.state = state

    def register(self, component):
        # Add the component to the set of components.
        self.components.append(component)

    def render(self):
        # Render each of the components.
        self.screen.clear()
        for component in self.components:
            component.draw()
        self.screen.refresh()

    @abstractmethod
    def open(self):
        pass


class ModelPage(Page):
    def __init__(self, screen, state):
        super().__init__(screen, state)

        # Initialize components.
        self.model_choice = ChoiceComponent(
            screen, 2, 1, [], escapes=(ord('q'), ord('n'))
        )
        self.register(ToolbarComponent(
            screen, 0, 0, {
                'N': 'New Model'
            }
        ))
        self.register(ToolbarComponent(
            screen, -1, 0, {
                'Q': 'Back',
                'Enter': 'Select'
            }
        ))
        self.register(self.model_choice)

    def open(self):
        while True:
            # Wait for a choice to be made.
            choice = None
            while choice is None:
                self.render()
                choice = self.model_choice.input()

            # Check for escape codes.
            if choice == ord('q'):
                return
            elif choice == ord('q'):
                pass


class GridPage(Page):
    def __init__(self, screen, state):
        super().__init__(screen, state)

    def open(self):
        pass


class MainPage(Page):
    def __init__(self, screen, state):
        super().__init__(screen, state)

        # Initialize components.
        self.object_choice = ChoiceComponent(
            screen, 1, 1, [
                "Models",
                "Grids",
                "Solvers",
                "Simulations"
            ], escapes=(ord('q'),))
        self.register(ToolbarComponent(
            screen, -1, 0, {
                'Q': 'Exit',
                'Enter': 'Select'
            }
        ))
        self.register(self.object_choice)

    def open(self):
        while True:
            # Wait for a choice to be made.
            choice = None
            while choice is None:
                self.render()
                choice = self.object_choice.input()

            # Check for escape codes.
            if choice == ord('q'):
                return

            # Open a new page based on the choice.
            _, name = choice
            page = None
            if name == "Models":
                page = ModelPage(self.screen, self.state)
            elif name == "Grids":
                page = GridPage(self.screen, self.state)
            elif name == "Solvers":
                pass
            elif name == "Simulations":
                pass
            page.open()


def main(stdscr):
    # Set colors.
    curses.start_color()
    curses.init_pair(ScreenColor.TOOLBAR,                       # Toolbar is black on white.
                     curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(ScreenColor.FORM,                          # Form is white on black.
                     curses.COLOR_WHITE, curses.COLOR_BLACK)

    # Create and load program state.
    state = ProgramState()
    state.load()

    # Create and run the main page.
    main_page = MainPage(stdscr, state)
    main_page.open()

    # Save the program state.
    state.save()


if __name__ == '__main__':
    wrapper(main)
