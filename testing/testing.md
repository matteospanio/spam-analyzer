# Testing

Tests are a great way to ensure that your code is working as expected, and that it continues to work as expected as you make changes to your code.

For a better development flow I suggest to follow the TDD paradigm (_Test Driven Development_), it consists in writing tests before implementing functionalities in a top-down approach to programming. Anyway, even if you don't follow the TDD rules you should provide tests for the code you write.

## Strategies

1. **Bottom-up**: every single components should have a unit test covering its base and limit cases and then 

2. **Black-box**: after testing how the code works we should ensure that it actually works, so at the end of the testing we consider the requirements and see if they are respected.

## Automation

The test suite is automated with [pytest](https://docs.pytest.org), to run tests go to the root directory of the project and type `make test`, the makefile will handle the tests launch with proper options; otherwise you can just open the console and run `pytest`. Pytest will automatically generate cache foldes and files, to delete them you can type `make clean`.
