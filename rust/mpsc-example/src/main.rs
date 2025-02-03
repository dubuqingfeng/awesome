use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use std::sync::mpsc;

// 定义任务类型
type Task = Box<dyn FnOnce() + Send + 'static>;

// 线程池结构体
struct ThreadPool {
    workers: Vec<Worker>,
    sender: mpsc::Sender<Task>,
}

// 工作线程结构体
struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

impl ThreadPool {
    // 创建线程池
    fn new(size: usize) -> Self {
        assert!(size > 0);

        let (sender, receiver) = mpsc::channel();
        let receiver = Arc::new(Mutex::new(receiver));

        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }

        ThreadPool { workers, sender }
    }

    // 执行任务
    fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let task = Box::new(f);
        self.sender.send(task).unwrap();
    }
}

impl Worker {
    // 创建工作线程
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Task>>>) -> Self {
        let thread = thread::spawn(move || loop {
            let task = receiver.lock().unwrap().recv();

            match task {
                Ok(task) => {
                    println!("Worker {} got a task; executing.", id);
                    task();
                }
                Err(_) => {
                    println!("Worker {} disconnected; shutting down.", id);
                    break;
                }
            }
        });

        Worker {
            id,
            thread: Some(thread),
        }
    }
}

impl Drop for ThreadPool {
    // 清理线程池
    fn drop(&mut self) {
        for worker in &mut self.workers {
            println!("Shutting down worker {}", worker.id);

            if let Some(thread) = worker.thread.take() {
                thread.join().unwrap();
            }
        }
    }
}

fn main() {
    // 创建线程池
    let pool = ThreadPool::new(4);

    // 共享状态
    let counter = Arc::new(Mutex::new(0));

    // 提交任务
    for i in 0..10 {
        let counter = Arc::clone(&counter);

        pool.execute(move || {
            let mut num = counter.lock().unwrap();
            *num += i;
            println!("Task {}: counter = {}", i, *num);
            thread::sleep(Duration::from_millis(200));
        });
    }

    // 等待任务完成
    thread::sleep(Duration::from_secs(2));

    // 输出最终结果
    println!("Final counter value: {}", *counter.lock().unwrap());
}