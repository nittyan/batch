# -*- coding: utf-8 -*-
from typing import Generic
from typing import List
from typing import TypeVar


O = TypeVar('O')               # batch output type
P = TypeVar('P')               # batch parameter type
R = TypeVar('R')               # task result type
TP = TypeVar('TP')
TR = TypeVar('TR')
T = TypeVar('T', bound='Task[TP, TR]')


class Job:

    def __init__(self, name: str):
        self._name = name

    def run(self):
        pass


class Converter(Generic[R, O]):

    def convert(self, r: R) -> O:
        pass


class SimpleJob(Generic[P, O], Job):

    def __init__(self, name: str, parameters: List[P], task: T, converter: Converter[TR, O]):
        super().__init__(name)
        self._parameters = parameters
        self._task = task
        self._converter = converter

    def run(self) -> List[O]:
        """
        simplest default implementation
        :return:
        """
        try:
            return [self._converter.convert(self._task.execute(p)) for p in self._parameters]
        except Exception as e:
            raise BatchError()

    @property
    def name(self):
        return self._name


class Task(Generic[P, R]):

    def execute(self, param: P) -> R:
        pass


class JobGroup(Job):
    """
    Jobs that were added in this object will be run in order.
    """

    def __init__(self, name: str, jobs: List[Job]):
        super().__init__(name)
        self._jobs = jobs

    def run(self):
        for job in self._jobs:
            job.run()

    @property
    def name(self):
        return self._name


class ParallelJobGroup(JobGroup):

    def __init__(self, name: str):
        super().__init__(name)

    def run(self):
        pass


class BatchError(Exception):
    pass