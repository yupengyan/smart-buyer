#!/bin/python
from fabric.api import local, settings, abort, run, cd
from fabric.api import task
from fabric.api import env
from fabric.operations import sudo
from fabric.contrib.console import confirm
from fabric.colors import green

def easyinstall(libname):
    with settings(warn_only=True):
        sudo("easy_install %s" % libname)
        print(green("success install %s" % libname))

@task
def pymmseg():
    """
    install pymmseg-cpp
    https://github.com/pluskid/pymmseg-cpp/
    """
    easyinstall('pymmseg-cpp')

@task
def pyredis():
    """
    install python redis client
    """
    easyinstall('redis')

@task
def pymongo():
    """
    install python mongo client
    """
    easyinstall("pymongo")

@task
def pil():
    """
    install python image library
    """
    easyinstall("PIL")

@task
def googleChartWrapper():
    easyinstall("GChartWrapper")

@task
def solrpy():
    """
    install solr python client
    """
    easyinstall("solrpy")

@task
def scrapy():
    """
    install scrapy
    """
    easyinstall("scrapy")

@task(default=True)
def all():
    """
    install all python dependencies
    """
    pyredis()
    pymongo()
    pil()
    googleChartWrapper()
    solrpy()