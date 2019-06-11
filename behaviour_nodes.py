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


class rootLoop(task):
    """
        Loop over one or more subtasks for the given number of iterations
        Use the value -1 to indicate a continual loop.
    """
    def __init__(self, name, findBestTarget, *args, **kwargs):
        super(rootLoop, self).__init__(name, *args, **kwargs)
        self.findBestTarget = findBestTarget
        # self.iterations = 1
        # self.loop_count = 0
        self.name = name

    def run(self):
        for c in self.children:
            if c == self.children[0]:
                self.findBestTarget.target = None
            c.run()
        return TaskStatus.SUCCESS


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


class RandomTargetInRange(task):
    target = None

    def __init__(self, name, player, asteroids, *args, **kwargs):
        self.player = player
        self.asteroids = asteroids
        super(RandomTargetInRange, self).__init__(name, *args, **kwargs)

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
        if self.direction == -1:
            self.player.moveLeft()
        elif self.direction == 1:
            self.player.moveRight()
        return TaskStatus.SUCCESS


class findBestTarget(task):
    target = None
    targetdirection = 0

    def __init__(self, name, player, asteroids, *args, **kwargs):
        super(findBestTarget, self).__init__(name, *args, **kwargs)
        self.asteroids = asteroids
        self.player = player

    def run(self):
        if self.target is not None:
            delta_y = self.player.y + 5 - self.target.y - 9 - self.target.height
            if delta_y <= 0:
                self.target = None
        if self.target is None:
            print('searching for target')
            minm = 100000
            for asteroid in self.asteroids:
                tempdirn = 1
                delta_x = asteroid.x + asteroid.width//2 - self.player.x - 5 - self.player.width//2
                if delta_x < 0:
                    tempdirn = -1
                    delta_x = (-delta_x)
                # delta_x += (asteroid.width//2 + self.player.width//2)
                delta_y = self.player.y + 5 - asteroid.y - 9 - asteroid.height

                if delta_y > 0 and delta_x * asteroid.vel < delta_y * self.player.vel:
                    if delta_y/asteroid.vel + 20 * delta_x/self.player.vel < minm:
                        minm = delta_y/asteroid.vel
                        self.target = asteroid
                        self.targetdirection = tempdirn

        if self.target is None:
            self.targetdirection = 0
            return TaskStatus.FAILURE
        else:
            print('Target Found')
            return TaskStatus.SUCCESS


class TargetInRange(task):

    def __init__(self, name, player, findTarget, *args, **kwargs):
        super(TargetInRange, self).__init__(name, *args, **kwargs)
        self.player = player
        self.findTarget = findTarget

    def run(self):
        bullet_x = self.player.x + self.player.width // 2 + 5
        target = self.findTarget.target
        if target is not None:
            if bullet_x > target.x and bullet_x < target.x + target.width:
                return TaskStatus.SUCCESS
            else:
                print("going to approach")
                return TaskStatus.FAILURE


class ApproachTarget(task):

    def __init__(self, name, player, findTarget, *args, **kwargs):
        super(ApproachTarget, self).__init__(name, *args, **kwargs)
        self.player = player
        self.findTarget = findTarget

    def run(self):
        print('approaching')
        direction = self.findTarget.targetdirection
        if direction != 0:
            # print(direction)
            self.player.x += direction * self.player.vel

class CheckLeft(task):

    def __init__(self, name, player, asteroids, *args, **kwargs):
        super(CheckLeft, self).__init__(name, *args, **kwargs)
        self.player = player
        self.asteroids = asteroids
        self.nearestObstacleDist = 100000

    def run(self):
        self.nearestObstacleDist = 100000
        for asteroid in self.asteroids:
            delta_y = self.player.y + 5 - asteroid.y - 9 - asteroid.height
            # bullet_x = self.player.x + self.player.width // 2 + 5
            delta_x = self.player.x + 5 + self.player.width // 2 - asteroid.x - asteroid.width//2
            if 0 < delta_x < (self.player.width + asteroid.width)//2 + 15:
                if delta_y * self.player.vel < asteroid.vel * ((self.player.width + asteroid.width)//2 - delta_x + 30):
                    if self.nearestObstacleDist > delta_y:
                        self.nearestObstacleDist = delta_y

        if self.nearestObstacleDist == 100000:
            return TaskStatus.FAILURE
        else:
            return TaskStatus.SUCCESS


class CheckRight(task):

    def __init__(self, name, player, asteroids, *args, **kwargs):
        super(CheckRight, self).__init__(name, *args, **kwargs)
        self.player = player
        self.asteroids = asteroids
        self.nearestObstacleDist = 100000

    def run(self):
        self.nearestObstacleDist = 100000
        for asteroid in self.asteroids:
            delta_y = self.player.y + 5 - asteroid.y - 9 - asteroid.height
            # bullet_x = self.player.x + self.player.width // 2 + 5
            delta_x = asteroid.x + asteroid.width//2 - self.player.x - 5 - self.player.width // 2
            if 0 < delta_x < (self.player.width + asteroid.width)//2 + 15:
                if delta_y * self.player.vel < asteroid.vel * ((self.player.width + asteroid.width)//2 - delta_x + 30):
                    if self.nearestObstacleDist > delta_y:
                        self.nearestObstacleDist = delta_y

        if self.nearestObstacleDist == 100000:
            return TaskStatus.FAILURE
        else:
            return TaskStatus.SUCCESS


class MoveBest(task):

    def __init__(self, name, player, leftNearest, rightNearest, *args, **kwargs):
        super(MoveBest, self).__init__(name, *args, **kwargs)
        self.player = player
        self.leftNearest = leftNearest
        self.rightNearest = rightNearest

    def run(self):
        if self.player.x + 15 <= self.player.width:
            self.player.moveRight()
        elif self.player.x + 15 + self.player.width > 900:
            self.player.moveLeft()
        elif self.leftNearest.nearestObstacleDist > self.rightNearest.nearestObstacleDist:
            self.player.moveLeft()
        else:
            self.player.moveRight()
        return TaskStatus.SUCCESS

