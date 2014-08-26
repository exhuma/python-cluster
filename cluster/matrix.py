
import logging
from multiprocessing import Process, Queue, current_process


logger = logging.getLogger(__name__)


class Matrix(object):
    """Object representation of the item-item matrix
    """

    def __init__(self, data, combinfunc, symmetric=False, diagonal=None):
        """Takes a list of data and generates a 2D-matrix using the supplied
        combination function to calculate the values.

        PARAMETERS
            data        - the list of items
            combinfunc  - the function that is used to calculate teh value in a
                          cell.  It has to cope with two arguments.
            symmetric   - Whether it will be a symmetric matrix along the diagonal.
                          For example, if the list contains integers, and the
                          combination function is abs(x-y), then the matrix will
                          be symmetric.
                          Default: False
            diagonal    - The value to be put into the diagonal. For some
                          functions, the diagonal will stay constant. An example
                          could be the function "x-y". Then each diagonal cell
                          will be "0".  If this value is set to None, then the
                          diagonal will be calculated.  Default: None
        """
        self.data = data
        self.combinfunc = combinfunc
        self.symmetric = symmetric
        self.diagonal = diagonal

    def worker(self):
        """Multiprocessing task function run by worker processes
        """
        tasks_completed = 0
        for task in iter(self.task_queue.get, 'STOP'):
            col_index, item, item2 = task
            result = (col_index, self.combinfunc(item, item2))
            self.task_queue.task_done()
            self.done_queue.put(result)
            tasks_completed += 1
        self.task_queue.task_done()
        logger.info("Worker %s performed %s tasks",
                    current_process().name,
                    tasks_completed)

    def genmatrix(self, num_processes=1):
        """Actually generate the matrix

        PARAMETERS
            num_processes
                        - If you want to use multiprocessing to split up the work
                          and run combinfunc() in parallel, specify num_processes
                          > 1 and this number of workers will be spun up, the work
                          split up amongst them evenly. Default: 1
        """
        use_multiprocessing = num_processes > 1
        if use_multiprocessing:
            self.task_queue = Queue()
            self.done_queue = Queue()

        self.matrix = []
        logger.info("Generating matrix for %s items - O(n^2)", len(self.data))
        if use_multiprocessing:
            logger.info("Using multiprocessing on %s processes!", num_processes)

        if use_multiprocessing:
            logger.info("Spinning up %s workers", num_processes)
            processes = [Process(target=self.worker) for i in range(num_processes)]
            [process.start() for process in processes]

        for row_index, item in enumerate(self.data):
            logger.debug("Generating row %s/%s (%0.2f%%)",
                         row_index,
                         len(self.data),
                         100.0 * row_index / len(self.data))
            row = {}
            if use_multiprocessing:
                num_tasks_queued = num_tasks_completed = 0
            for col_index, item2 in enumerate(self.data):
                if self.diagonal is not None and col_index == row_index:
                    # This is a cell on the diagonal
                    row[col_index] = self.diagonal
                elif self.symmetric and col_index < row_index:
                    # The matrix is symmetric and we are "in the lower left
                    # triangle" - fill this in after (in case of multiprocessing)
                    pass
                # Otherwise, this cell is not on the diagonal and we do indeed
                # need to call combinfunc()
                elif use_multiprocessing:
                    # Add that thing to the task queue!
                    self.task_queue.put((col_index, item, item2))
                    num_tasks_queued += 1
                    # Start grabbing the results as we go, so as not to stuff all of
                    # the worker args into memory at once (as Queue.get() is a
                    # blocking operation)
                    if num_tasks_queued > num_processes:
                        col_index, result = self.done_queue.get()
                        self.done_queue.task_done()
                        row[col_index] = result
                        num_tasks_completed += 1
                else:
                    # Otherwise do it here, in line
                    row[col_index] = self.combinfunc(item, item2)

            if self.symmetric:
                # One more iteration to get symmetric lower left triangle
                for col_index, item2 in enumerate(self.data):
                    if col_index >= row_index:
                        break
                    # post-process symmetric "lower left triangle"
                    row[col_index] = self.matrix[col_index][row_index]

            if use_multiprocessing:
                # Grab the remaining worker task results
                while num_tasks_completed < num_tasks_queued:
                    col_index, result = self.done_queue.get()
                    self.done_queue.task_done()
                    row[col_index] = result
                    num_tasks_completed += 1

            row_indexed = [row[index] for index in range(len(self.data))]
            self.matrix.append(row_indexed)

        if use_multiprocessing:
            logger.info("Stopping/joining %s workers", num_processes)
            [self.task_queue.put('STOP') for i in range(num_processes)]
            [process.join() for process in processes]

        logger.info("Matrix generated")

    def __str__(self):
        """
        Prints out a 2-dimensional list of data cleanly.
        This is useful for debugging.

        PARAMETERS
            data  -  the 2D-list to display
        """
        # determine maximum length
        maxlen = 0
        colcount = len(self.data[0])
        for col in self.data:
            for cell in col:
                maxlen = max(len(str(cell)), maxlen)
        format = " %%%is |" % maxlen
        format = "|" + format * colcount
        rows = [format % tuple(row) for row in self.data]
        return "\n".join(rows)
