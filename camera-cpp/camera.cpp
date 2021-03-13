#include "camera.h"
#include "ui_mainwindow.h"
#include <sys/stat.h>

static CvMemStorage* storage = 0;
static CvHaarClassifierCascade* cascade = 0;

void detect_and_draw(IplImage* image);

camera::camera(QMainWindow *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    cascade_name = "haarcascade_frontalface_alt2.xml";

    struct stat buf;
    int statResult = stat(cascade_name, &buf);
    if (statResult || buf.st_ino < 0) {
        fprintf( stderr, "ERROR: Could not load classifie cascade\n" );
        exit(-2);
    }

    cascade = (CvHaarClassifierCascade*)cvLoad( cascade_name, 0, 0, 0 );
    if( !cascade )
    {
        fprintf( stderr, "ERROR: Could not load classifier cascade\n" );
    }

    storage = cvCreateMemStorage(0);

    cam     = NULL;
    timer   = new QTimer(this);
    imag    = new QImage();

    /*信号槽*/
    connect(timer, SIGNAL(timeout()), this, SLOT(readFarme()));  // 时间到，读取当前摄像头信息
    connect(ui->open, SIGNAL(clicked()), this, SLOT(openCamara()));
    connect(ui->pic, SIGNAL(clicked()), this, SLOT(takingPictures()));
    connect(ui->closeCam, SIGNAL(clicked()), this, SLOT(closeCamara()));
}

void camera::openCamara()
{
    cam = cvCreateCameraCapture(0);
    timer->start(33);
}

void camera::readFarme()
{
    frame = cvQueryFrame(cam);// 从摄像头中抓取并返回每一帧
    detect_and_draw(frame);
    // 将抓取到的帧，转换为QImage格式。QImage::Format_RGB888不同的摄像头用不同的格式。
    //    QImage image((const uchar*)frame->imageData, frame->width, frame->height, QImage::Format_RGB888);
    QImage image = QImage((const uchar*)frame->imageData, frame->width, frame->height, QImage::Format_RGB888).rgbSwapped();

    ui->label->setPixmap(QPixmap::fromImage(image));  // 将图片显示到label上
}

void camera::takingPictures()
{
    frame = cvQueryFrame(cam);
    // 将抓取到的帧，转换为QImage格式。QImage::Format_RGB888不同的摄像头用不同的格式。
    QImage image((const uchar*)frame->imageData, frame->width, frame->height, QImage::Format_RGB888);
    ui->label_2->setPixmap(QPixmap::fromImage(image));  // 将图片显示到label上
}

void camera::closeCamara()
{
    timer->stop();         // 停止读取数据。
    cvReleaseCapture(&cam);//释放内存；
}

void detect_and_draw(IplImage* img)
{
    double scale=1.2;
//    static CvScalar colors[] = {
//        {{0,0,255}},{{0,128,255}},{{0,255,255}},{{0,255,0}},
//        {{255,128,0}},{{255,255,0}},{{255,0,0}},{{255,0,255}}
//    };//Just some pretty colors to draw with
    static CvScalar colors[] = {
        {0,0,255},{0,128,255},{0,255,255},{0,255,0},
        {255,128,0},{255,255,0},{255,0,0},{255,0,255}
    };//Just some pretty colors to draw with


    //Image Preparation
    //
    IplImage* gray = cvCreateImage(cvSize(img->width,img->height),8,1);
    IplImage* small_img=cvCreateImage(cvSize(cvRound(img->width/scale),cvRound(img->height/scale)),8,1);
    cvCvtColor(img,gray, CV_BGR2GRAY);
    cvResize(gray, small_img, CV_INTER_LINEAR);

    cvEqualizeHist(small_img,small_img); //直方图均衡

    //Detect objects if any
    //
    cvClearMemStorage(storage);
    double t = (double)cvGetTickCount();
    CvSeq* objects = cvHaarDetectObjects(small_img,
                                         cascade,
                                         storage,
                                         1.1,
                                         2,
                                         0/*CV_HAAR_DO_CANNY_PRUNING*/,
                                         cvSize(30,30));

    t = (double)cvGetTickCount() - t;
    printf( "detection time = %gms\n", t/((double)cvGetTickFrequency()*1000.) );

    //Loop through found objects and draw boxes around them
    for(int i=0;i<(objects? objects->total:0);++i)
    {
        CvRect* r=(CvRect*)cvGetSeqElem(objects,i);
        cvRectangle(img, cvPoint(r->x*scale,r->y*scale), cvPoint((r->x+r->width)*scale,(r->y+r->height)*scale), colors[i%8]);
    }
    for( int i = 0; i < (objects? objects->total : 0); i++ )
    {
        CvRect* r = (CvRect*)cvGetSeqElem( objects, i );
        CvPoint center;
        int radius;
        center.x = cvRound((r->x + r->width*0.5)*scale);
        center.y = cvRound((r->y + r->height*0.5)*scale);
        radius = cvRound((r->width + r->height)*0.25*scale);
        cvCircle( img, center, radius, colors[i%8], 3, 8, 0 );
    }

    cvShowImage( "result", img );
    cvReleaseImage(&gray);
    cvReleaseImage(&small_img);
}

camera::~camera()
{
    delete ui;
}
