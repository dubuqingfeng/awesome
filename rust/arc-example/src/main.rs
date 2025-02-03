use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    // 创建一个 Arc 包装 Mutex
    let data = Arc::new(Mutex::new(0));

    let mut handles = vec![];

    for i in 0..5 {
        let data_clone = Arc::clone(&data);

        let handle = thread::spawn(move || {
            // 锁定 Mutex 以修改数据
            let mut num = data_clone.lock().unwrap();
            *num += i;
            println!("Thread {}: data = {}", i, *num);
        });

        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Final data: {}", *data.lock().unwrap());
}