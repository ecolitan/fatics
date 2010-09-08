#!/bin/sh
twistd --pidfile chessd.pid -r epoll -noy src/chessd.tac
#rm -f twistd.log ; twistd --pidfile chessd.pid -r epoll -oy src/chessd.tac
#twistd --profile profile-chessd.data --savestats --profiler cProfile -r epoll -noy src/chessd.tac
