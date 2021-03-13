#-------------------------------------------------
#
# Project created by QtCreator 2017-05-29T16:10:56
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = camera
TEMPLATE = app

# The following define makes your compiler emit warnings if you use
# any feature of Qt which as been marked as deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0


SOURCES += main.cpp\
        mainwindow.cpp \
    camera.cpp

HEADERS  += mainwindow.h \
    camera.h

FORMS    += mainwindow.ui

DISTFILES += \
    haarcascade_frontalface_alt.xml \
    haarcascade_frontalface_alt2.xml

RESOURCES += \
    menu_icon.qrc

#INCLUDEPATH +=/usr/local/opt/opencv3/include/opencv2
INCLUDEPATH += /usr/local/Cellar/opencv/2.4.13.2/include/opencv2

QT_CONFIG -= no-pkg-config
CONFIG  += link_pkgconfig
PKGCONFIG += opencv
