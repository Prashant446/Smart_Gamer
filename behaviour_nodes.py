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


class Selector(task):
    """
    Run each subtask in sequence until one succeeds or we run out of tasks.
    """
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def run(self):
        for c in self.children:
            c.status = c.run()
            if c.status != TaskStatus.FAILURE:
                return c.status
        return TaskStatus.FAILURE


class Sequence(task):
    """
    Run each subtask in sequence until one fails or we run out of tasks.
    """
    def __init__(self, name, *args, **kwargs):
        super(Sequence, self).__init__(name, *args, **kwargs)

    def run(self):
        for c in self.children:
            c.status = c.run()
            if c.status != TaskStatus.SUCCESS:
                return c.status
        return TaskStatus.SUCCESS


class Iterator(task):
    """
    Iterate through all child tasks ignoring failure.
    """
    def __init__(self, name, *args, **kwargs):
        super(Iterator, self).__init__(name, *args, **kwargs)

    def run(self):
        for c in self.children:
            c.status = c.run()
            if c.status != TaskStatus.SUCCESS and c.status != TaskStatus.FAILURE:
                return c.status
        return TaskStatus.SUCCESS


class ParallelOne(task):
    """
    A parallel task runs each child task at (roughly) the same time.
    The ParallelOne task returns success as soon as any child succeeds.
    """
    def __init__(self, name, *args, **kwargs):
        super(ParallelOne, self).__init__(name, *args, **kwargs)

    def run(self):
        for c in self.children:
            c.status = c.run()
            if c.status == TaskStatus.SUCCESS:
                return TaskStatus.SUCCESS
        return TaskStatus.FAILURE


class ParallelAll(task):
    """
    A parallel task runs each child task at (roughly) the same time.
    The ParallelAll task requires all subtasks to succeed for it to succeed.
    """
    def __init__(self, name, *args, **kwargs):
        super(ParallelAll, self).__init__(name, *args, **kwargs)

    def run(self):
        n_success = 0
        n_children = len(self.children)
        for c in self.children:
            c.status = c.run()
            if c.status == TaskStatus.SUCCESS:
                n_success += 1
            if c.status == TaskStatus.FAILURE:
                return TaskStatus.FAILURE
        if n_success == n_children:
            return TaskStatus.SUCCESS
        else:
            return TaskStatus.RUNNING


class Loop(task):
    """
        Loop over one or more subtasks for the given number of iterations
        Use the value -1 to indicate a continual loop.
    """
    def __init__(self, name, announce=True, *args, **kwargs):
        super(Loop, self).__init__(name, *args, **kwargs)

        self.iterations = kwargs['iterations']
        self.announce = announce
        self.loop_count = 0
        self.name = name
        print("Loop iterations: " + str(self.iterations))

    def run(self):

        while True:
            if self.iterations != -1 and self.loop_count >= self.iterations:
                return TaskStatus.SUCCESS

            for c in self.children:
                while True:
                    c.status = c.run()

                    if c.status == TaskStatus.SUCCESS:
                        break
                    return c.status
                c.reset()

            self.loop_count += 1

            if self.announce:
                print(self.name + " COMPLETED " + str(self.loop_count) + " LOOP(S)")


class IgnoreFailure(task):
    """
    Always return either RUNNING or SUCCESS.
    """
    def __init__(self, name, *args, **kwargs):
        super(IgnoreFailure, self).__init__(name, *args, **kwargs)

    def run(self):
        for c in self.children:
            c.status = c.run()
            if c.status != TaskStatus.RUNNING:
                return TaskStatus.SUCCESS
            else:
                return TaskStatus.RUNNING
        return TaskStatus.SUCCESS


class AttackSequence(task):

    def __init__(self, name, *args, **kwargs):
        super(AttackSequence, self).__init__(name, *args, **kwargs)

    def run(self):
        for c in self.children:
            c.status = c.run()
            if c.status != TaskStatus.SUCCESS:
                return c.status
        self.children[0].target.healthPredictor -= 150
        return TaskStatus.SUCCESS


class FireNode(task):

    def __init__(self, name, player, *args, **kwargs):
        self.player = player
        super(FireNode, self).__init__(name, *args, **kwargs)

    def run(self):
        if self.player.fire():
            return TaskStatus.SUCCESS
        return TaskStatus.FAILURE


class TargetInRange(task):
    target = None

    def __init__(self, name, player, asteroids, *args, **kwargs):
        self.player = player
        self.asteroids = asteroids
        super(TargetInRange, self).__init__(name, *args, **kwargs)

    def run(self):
        bullet_x = self.player.x + self.player.width//2 + 5
        for asteroid in self.asteroids:
            if bullet_x > asteroid.x and bullet_x < asteroid.x + asteroid.width and asteroid.healthPredictor >= 0:
                self.target = asteroid
                return TaskStatus.SUCCESS
        return TaskStatus.FAILURE


class Move(task):

    def __init__(self, name, direction, player, *args, **kwargs):
        super(Move, self).__init__(name, *args, **kwargs)
        self.direction = direction
        self.player = player

    def run(self):
        if self.direction == 1:
            self.player.moveLeft()
        elif self.direction == -1:
            self.player.moveRight()
