class TaskStatus:
    FAILURE = 0
    SUCCESS = 1
    RUNNING = 2


class task:

    def __init__(self, name, children=None):
        self.name = name
        self.status = None
        if children is None:
            children = []
        self.children = children

    def run(self):
        pass

    def reset(self):
        for c in self.children:
            c.reset()

    def insert_child(self, child, index):
        self.children.insert(index, child)

    def remove_child(self, c):
        self.children.remove(c)

    def prepend_child(self, c):
        self.children.insert(0, c)

    def add_child(self, c):
        self.children.append(c)

    def get_status(self):
        return self.status

    def set_status(self, s):
        self.status = s

    def announce(self):
        print("Executing task " + str(self.name))

    # These next two functions allow us to use the 'with' syntax
    def __enter__(self):
        return self.name

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            return False
        return True


