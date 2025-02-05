class LogsCollector:
    def __init__(self, print_log: bool = True):
        """
        This class is used for collecting logs.

        Use the add() function to print the log and store it in a list.
        Use the get() function to get all the logs collected.

        :param print_log: Whether to print the log on add().
        """

        self.__print_log = print_log
        self.__logs: list[str] = []

    def add(self, log: str) -> None:
        """
        Add log to list and print log.
        """

        self.__logs.append(log)

        if self.__print_log:
            print(log)

    def get(self) -> list[str]:
        """
        Get list of logs.
        """

        return self.__logs
