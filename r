#!/bin/sh
twistd --pidfile chessd.pid -r epoll -noy src/chessd.tac
#twistd --profile profile-chessd.data --savestats --profiler cProfile -r epoll -noy src/chessd.tac
