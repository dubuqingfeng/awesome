#ifndef CAMERA_H
#define CAMERA_H

#include <QMainWindow>
#include <QImage>
#include <QTimer>

#include <highgui.h>
#include <cv.h>

namespace Ui {
class MainWindow;
}

class camera : public QMainWindow
{
    Q_OBJECT

public:
    explicit camera(QMainWindow *parent = 0);
    ~camera();

private slots:
    void openCamara();      // 打开摄像头
    void readFarme();       // 读取当前帧信息
    void closeCamara();     // 关闭摄像头。
    void takingPictures();  // 拍照

private:
    Ui::MainWindow *ui;
    QTimer    *timer;
    QImage    *imag;
    const char* cascade_name;
    CvCapture *cam;// 视频获取结构， 用来作为视频获取函数的一个参数
    IplImage  *frame;//申请IplImage类型指针，就是申请内存空间来存放每一帧图像
};

#endif // CAMERA_H
